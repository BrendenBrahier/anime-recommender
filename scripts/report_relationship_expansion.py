"""Compare saved service checks and summarize relationship evidence coverage."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from expand_relationships import popular_ids
from build_relationships import ROOT
from enrich_catalog import save
from recommendation_engine import content_reasons, relationship_reasons
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--before-relationships', type=Path)
    args = parser.parse_args()
    catalog = json.loads((ROOT / 'data/current/catalog.json').read_text(encoding='utf-8'))
    records = json.loads((ROOT / 'data/current/relationships.json').read_text(encoding='utf-8'))['records']
    before = json.loads(args.before.read_text(encoding='utf-8'))
    after = json.loads((ROOT / 'evaluation/results/service_checks.json').read_text(encoding='utf-8'))
    if before.get('watch_order_policy_sha256') or after.get('watch_order_policy_sha256'):
        raise SystemExit('This historical expansion comparison requires source-only checks. Use check_watch_order.py for the reviewed policy audit.')
    verified = {k for k, r in records.items() if r['verified_relations']}
    catalog_ids = {r['anime_id'] for r in catalog}
    def summary(check):
        return {**check['summary'], 'distinct_recommendations': len({r['anime_id'] for run in check['runs'] for r in run['results']})}
    old = {run['case_id']: run for run in before['runs']}
    comparisons = []
    for run in after['runs']:
        previous = old[run['case_id']]['results']
        previous_ids = {r['anime_id'] for r in previous}
        current_ids = {r['anime_id'] for r in run['results']}
        comparisons.append({'case_id': run['case_id'], 'before_count': len(previous),
                            'after_count': len(run['results']),
                            'added_ids': sorted(current_ids - previous_ids),
                            'removed_ids': sorted(previous_ids - current_ids)})
    popularity = []
    for n in [100, 1000, 5000]:
        targets = {f'mal:{mid}' for mid in popular_ids(catalog, n)}
        popularity.append({'top': n, 'targeted': len(targets), 'verified': len(targets & verified)})
    eras = {}
    for row in catalog:
        year = row.get('year')
        era = str(int(year) // 10 * 10) + 's' if year else 'unknown'
        counts = eras.setdefault(era, {'catalog': 0, 'verified': 0})
        counts['catalog'] += 1
        counts['verified'] += row['anime_id'] in verified
    missing_neighbors = sorted({edge['anime_id'] for key in verified for edge in records[key]['relations']
                                if edge['anime_id'] not in verified})
    result = {'built_utc': datetime.now(timezone.utc).isoformat(),
              'before': summary(before), 'after': summary(after),
              'popular_coverage': popularity, 'eras': dict(sorted(eras.items())),
              'recap_status_catalog_verified': dict(Counter(records[k]['recap_status'] for k in verified & catalog_ids)),
              'verified_titles_outside_catalog': len(verified - catalog_ids),
              'unverified_anime_neighbors_all_relation_types': missing_neighbors,
              'cases': comparisons,
              'limitations': ['No independent relevance grading; result changes are not proof of improved accuracy.',
                              'Popularity uses the existing catalog snapshot, not a newly fetched ranking.',
                              'Relationship evidence is source metadata, not a curated watch-order guarantee.',
                              'Canonical catalog and saved notebook outputs were not changed.']}
    def starting_candidates(evidence):
        return sum(not content_reasons(row, {}) and
                   not relationship_reasons(row['anime_id'], evidence, set()) for row in catalog)
    result['strict_starting_candidates_after'] = starting_candidates(records)
    result['unverified_prerequisite_ids'] = sorted({p for r in records.values()
                                                   for p in r.get('prerequisites', []) if p not in verified})
    result['cycle_or_depth_limit_ids'] = sorted(k for k, r in records.items()
        if r.get('prerequisites') and 'cyclic_prerequisites' in
        relationship_reasons(k, records, set(), allow_recaps=True, allow_unknown=True))
    keys = sorted(records); positions = {k: i for i, k in enumerate(keys)}
    edges = [(positions[k], positions[p]) for k, r in records.items() for p in r['prerequisites']]
    graph = csr_matrix(([1] * len(edges), ([a for a, b in edges], [b for a, b in edges])),
                       shape=(len(keys), len(keys)))
    _, labels = connected_components(graph, directed=True, connection='strong')
    groups = {}
    for key, label in zip(keys, labels):
        groups.setdefault(int(label), []).append(key)
    titles = {r['anime_id']: r.get('name_english') or r.get('name') for r in catalog}
    review = []
    for members in groups.values():
        if len(members) == 1 and members[0] not in records[members[0]]['prerequisites']:
            continue
        internal = []
        for dependent in members:
            for required in records[dependent]['prerequisites']:
                if required not in members:
                    continue
                evidence = []
                for source, target, types in [(dependent, required, {'prequel', 'parent story'}),
                                               (required, dependent, {'sequel', 'side story'})]:
                    evidence += [{'source_id': source, 'target_id': target, 'relation': rel['type'],
                                  'source_url': records[source].get('source_url'),
                                  'retrieved_at': records[source].get('retrieved_at')}
                                 for rel in records[source]['relations']
                                 if rel['anime_id'] == target and rel['type'] in types]
                internal.append({'dependent_id': dependent, 'required_id': required, 'evidence': evidence})
        review.append({'members': [{'anime_id': k, 'title': titles.get(k)} for k in members],
                       'internal_dependencies': internal})
    result['prerequisite_cycle_groups'] = review
    if args.before_relationships:
        prior = json.loads(args.before_relationships.read_text(encoding='utf-8'))['records']
        result['strict_starting_candidates_before'] = starting_candidates(prior)
    save(ROOT / 'evaluation/results/relationship_expansion_comparison.json', result)
    lines = ['# Relationship coverage expansion', '',
             f"Generated {result['built_utc']} (UTC).", '',
             'The ranking algorithm and catalog are unchanged; only relationship evidence expanded.', '',
             '| Measure | Before | After |', '| --- | ---: | ---: |']
    for label, key in [('Verified catalog titles', 'verified_relationship_catalog_entries'),
                       ('Returned recommendation slots', 'returned'),
                       ('Requests receiving five results', 'requests_with_five_results'),
                       ('Recorded policy violations', 'violating_results'),
                       ('Distinct recommended titles', 'distinct_recommendations')]:
        lines.append(f"| {label} | {result['before'][key]} | {result['after'][key]} |")
    lines += ['', '## Popular-title coverage', '', '| Popularity group | Verified | Targeted |',
              '| --- | ---: | ---: |']
    lines += [f"| Top {r['top']} | {r['verified']} | {r['targeted']} |" for r in popularity]
    lines += ['', '## Release decades', '', '| Decade | Verified | Catalog |', '| --- | ---: | ---: |']
    lines += [f"| {era} | {counts['verified']} | {counts['catalog']} |" for era, counts in sorted(eras.items())]
    lines += ['', '## Interpretation', ''] + [f'- {text}' for text in result['limitations']]
    lines += ['', f"Strict policy-eligible starting titles after expansion: {result['strict_starting_candidates_after']}."]
    if 'strict_starting_candidates_before' in result:
        lines += [f"Before expansion: {result['strict_starting_candidates_before']}."]
    lines += ['These counts assume no completed prerequisites and default content/recap policies; they do not require a positive query match.']
    lines += ['', f"Unverified prerequisite IDs: {len(result['unverified_prerequisite_ids'])}.",
              f"Titles blocked by cyclic dependencies or the 100-level depth guard: {len(result['cycle_or_depth_limit_ids'])}.",
              f"Distinct prerequisite cycle groups: {len(review)}.",
              'The JSON comparison includes group members and the source evidence for every internal dependency.',
              'These are cycles in the derived prerequisite policy, not necessarily incorrect source records: chronological prequels and parent/side-story relationships do not always imply mandatory viewing order. The runtime keeps affected titles blocked pending watch-order review.']
    lines += ['', 'Detailed per-request changes are in `results/relationship_expansion_comparison.json`.',
              'Download coverage, unavailable records, errors, and pending IDs are in `results/relationship_coverage.json`.', '']
    (ROOT / 'evaluation/RELATIONSHIP_EXPANSION.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['before', 'after', 'popular_coverage', 'eras']}, indent=2))


if __name__ == '__main__':
    main()
