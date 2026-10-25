"""Summarize the benchmark without treating unjudged titles as known irrelevant."""
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def score(runs, judgments):
    lookup={(x['case_id'],x['anime_id']):x for x in judgments}
    rows=[]
    for model in sorted({r['model'] for r in runs}):
        selected=[r for r in runs if r['model']==model and r['supported']]
        items=[(r,x,lookup.get((r['case_id'],x['anime_id']),{}).get('grade')) for r in selected for x in r['results']]
        known=[g for _,_,g in items if g is not None]
        good=sum(g is not None and g>=2 for _,_,g in items)
        usable=sum(g is not None and g>=2 and not x['violations'] for _,x,g in items)
        slots=5*len(selected)
        rows.append({'model':model,'requests':len(selected),'returned':len(items),'judged':len(known),'unknown':len(items)-len(known),'mean_known_grade':round(sum(known)/len(known),3) if known else None,'plausible_or_strong_lower_bound':round(good/slots,4) if slots else None,'constraint_compliant_relevant_lower_bound':round(usable/slots,4) if slots else None})
    return rows

def main():
    folder=ROOT/'evaluation'; result=json.loads((folder/'results/benchmark.json').read_text(encoding='utf-8'))
    judgments=json.loads((folder/'initial_judgments.json').read_text(encoding='utf-8'))
    cases=json.loads((folder/'cases.json').read_text(encoding='utf-8'))
    if hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest()!=result['manifest']['cases_sha256']:
        raise ValueError('Cases changed since the benchmark run; regenerate results first.')
    if judgments.get('catalog_sha256') != result['manifest']['catalog_sha256'] or judgments.get('cases_sha256') != result['manifest']['cases_sha256']:
        raise ValueError('Judgments must match the exact catalog and case snapshot; review new results before reporting.')
    # Filter-only control is intentionally unjudged, avoiding selective partial labels.
    primary=[r for r in result['runs'] if r['model']!='legacy_filtered']
    paired=[r for r in primary if not r['case_id'].endswith('-5')]
    metrics={'all_supported':score(primary,judgments['annotations']),'matched_32_seed_requests':score(paired,judgments['annotations'])}
    metrics['cold_start_8']=score([r for r in primary if r['case_id'].endswith('-5')],judgments['annotations'])
    (folder/'results/relevance_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
    lines=['# Recommendation evaluation: first development benchmark','',
        'Snapshot: October 2026 catalog, 38,259 entries. Forty authored requests cover eight topics and five scenarios each: one liked title, a short completed TV series, a release-era range, multiple likes/dislikes and excluded categories, and a no-seed movie request. These are 40 variations of eight taste profiles, not 40 independent users.', '',
        '## Objective checks','', '| Method | Supported requests | Returned top-5 slots | Results violating constraints | Category diversity | Distinct titles |','|---|---:|---:|---:|---:|---:|']
    for name,s in result['summary'].items():
        lines.append(f"| {name} | {s['supported']}/40 | {s['returned']} | {s['violating_results']}/{s['returned']} ({s['violation_rate']:.1%}) | {s['category_diversity']:.3f} | {s['unique_titles']} |")
    lines+=['','Constraint checks use the current catalog, not independent verification of every episode count, genre, or status. Unknown constrained values fail closed. Explicit hentai is excluded, but the benchmark is not a general age-safety classifier. Diversity is pairwise category Jaccard distance: higher can also mean less relevant results. Distinct-title totals cover different numbers of supported requests; use matched cases for head-to-head comparisons.','',
        '## Provisional relevance on the same 32 seed requests','',
        '| Method | Judged / returned | Mean topical grade (0–3, known only) | Plausible-or-strong lower bound / all slots | Relevant AND constraint-compliant lower bound |','|---|---:|---:|---:|---:|']
    for s in metrics['matched_32_seed_requests']:
        lines.append(f"| {s['model']} | {s['judged']}/{s['returned']} | {s['mean_known_grade']:.3f} | {s['plausible_or_strong_lower_bound']:.1%} | {s['constraint_compliant_relevant_lower_bound']:.1%} |")
    lines+=['','Grades are an assistant first pass based on catalog synopsis excerpts and categories, with candidate model/rank hidden during review. The same assistant authored the cases and prototype, so these are not independent human judgments or proven recommendation accuracy. Grades describe topical fit; hard constraints are scored separately. Uncertain entries stay unknown and contribute no credit to lower bounds. Topic grades are reused across constraint variants. Soft-dislike satisfaction and prerequisite suitability are not numerically validated. The filter-only control is not relevance-graded.','',
        '## What to improve next','',
        '1. **Apply explicit filters first.** The filter-only control isolates this benefit; a new semantic model is not necessary to obey episode, format, era, completion, and seen-title constraints.',
        '2. **Add franchise relationships and recap flags.** Haikyu and Non Non Biyori lists concentrate on the same franchise; mystery results include Death Note recaps and later seasons. Exact-ID exclusions do not solve cross-provider duplicates or viewing order.',
        '3. **Improve tone matching and format defaults.** Cold-start calm requests return generic comedy shorts. Music requests can return music videos rather than stories about musicians. Topic overlap alone is insufficient.',
        '4. **Resolve sparse identities and audit metadata.** Source-only recommendations with empty synopses cannot be confidently judged. Filter correctness is only as strong as source metadata.',
        '5. **Collect independent human ratings before tuning.** Review the provisional labels, add genuinely new requests, and reserve a separate held-out set. Compare pretrained sentence embeddings with this inexpensive LSA baseline before adopting either.',
        '', '## Methods and reproducibility','',
        '- `legacy_cosine`: same TF-IDF feature construction and scaled score/membership cosine as the existing code, using current compatibility data. Computes one similarity row per seed instead of the full square matrix. Uses stable IDs and explicitly removes the seed; original title-collision behavior is not reproduced. Graph/hashmap dispatch is not evaluated; existing dispatch signatures/columns are inconsistent.',
        '- `legacy_filtered`: identical ranking with request filters, used as an objective control.',
        '- `hybrid`: synopsis TF-IDF plus 64-dimensional latent semantic analysis (LSA), category similarity, vote-shrunk MAL score, likes/dislikes, hard filters, and a modest diversity penalty. Weights fixed at .35 lexical, .30 LSA, .25 categories, .10 score; dislike penalty .15, diversity penalty .10. LSA is corpus-derived topic matching, not a pretrained language model. See [scikit-learn TruncatedSVD documentation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html).',
        '- Requests have explicitly authored structured filters and preferences. This benchmark does **not** test automatic natural-language parsing. Both ranking methods use the same catalog snapshot. No preference labels are used to train the topic model.',
        '- Development corrections before final results: fixed the calm-profile seed ID and made unknown excluded-category metadata fail closed. No ranking weights were tuned against the judgments.',
        '- Ranked result lists, source hashes, package versions, and random seed are in `results/benchmark.json`. Saved results are tied to local raw-source caches; a fresh source download may change them.',
        '', '```powershell', 'python -m pip install -r requirements-evaluation.txt', 'python scripts/evaluate_recommendations.py', 'python scripts/report_evaluation.py', 'python -m unittest discover -s tests -p test_evaluation.py -v', '```', '',
        'The evaluation command requires the generated `data/current` files (see DATA.md). The report command rejects judgments from another snapshot. `results/review.html` and `results/review_queue.json` are local review aids containing synopses; they are not published. Edit the separate `initial_judgments.json` labels with reviewer identity and reasoning when conducting human review. Running the benchmark does not overwrite those labels. Full result lists follow.','', '## Results for every request','']
    lookup={(j['case_id'],j['anime_id']):j for j in judgments['annotations']}
    for c in cases:
        lines.extend([f"### {c['id']}",'',c['prompt'],''])
        for run in [r for r in result['runs'] if r['case_id']==c['id']]:
            lines.append(f"**{run['model']}**"+' (unsupported without a seed)' if not run['supported'] else f"**{run['model']}**")
            lines.append('')
            for x in run['results']:
                label=lookup.get((c['id'],x['anime_id'])) if run['model']!='legacy_filtered' else None
                grade='not graded' if label is None else ('unknown' if label['grade'] is None else str(label['grade'])+'/3')
                audit=', '.join(x['violations']) or 'passes recorded constraints'
                lines.append(f"- {x['rank']}. {x['title']} ({x['anime_id']}) — {grade}; {audit}.")
            lines.append('')
    (folder/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
