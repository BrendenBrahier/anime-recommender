"""Audit the reviewed policy against real local evidence and retain a review log."""
import hashlib
import json
from pathlib import Path
from recommendation_engine import Recommender, relationship_reasons, content_reasons
from watch_order import load_policy
from enrich_catalog import save

ROOT=Path(__file__).resolve().parents[1]


def main():
    policy,policy_hash=load_policy()
    engine=Recommender.from_directory()
    raw=engine.source_relationships;effective=engine.relationships
    def blocked(records):
        return sorted(k for k in records if 'cyclic_prerequisites' in relationship_reasons(k,records,set()))
    before=blocked(raw);after=blocked(effective)
    def pool(records):
        return sum(not content_reasons(r,{}) and not relationship_reasons(r['anime_id'],records,set()) for r in engine.catalog)
    entries=sorted({k for g in policy['groups'] for k in g['entry_points']})
    assert all(not relationship_reasons(k,effective,set()) for k in entries), 'Entry-point policy regression'
    assert not after, 'Unresolved cycles require review; do not discard edges automatically'
    # Genuine sequel gates remain independently checked on real source records.
    for target,completed in [('mal:1735',{'mal:20'}),('mal:541',{'mal:540'}),
                             ('mal:41140',{'mal:37807'}),('mal:4918',{'mal:3091'}),('mal:4938',{'mal:2685'})]:
        assert 'unwatched_prerequisite' in relationship_reasons(target,effective,set())
        assert not relationship_reasons(target,effective,completed),target
    assert 'recap' in relationship_reasons('mal:4037',effective,set())
    assert effective['mal:80']['franchise_id']==effective['mal:55845']['franchise_id']
    summary={'policy_sha256':policy_hash,'reviewed_groups':len(policy['groups']),
             'decisions':sum(len(g['decisions']) for g in policy['groups']),
             'raw_cycle_blocked_titles':len(before),'effective_cycle_blocked_titles':len(after),
             'starting_candidates_before':pool(raw),'starting_candidates_after':pool(effective),
             'reviewed_entry_points':entries,'formerly_blocked_ids':before,
             'source_relationships_sha256':hashlib.sha256((ROOT/'data/current/relationships.json').read_bytes()).hexdigest(),
             'review_status':policy['review_status']}
    save(ROOT/'evaluation/results/watch_order_checks.json',summary)
    lines=['# Reviewed watch-order decisions','',
           'These are documented recommendation policies based on source metadata and editorial judgment. User validation is still pending.',
           'Raw source relationships and inferred prerequisites remain intact in data/current/relationships.json. The runtime applies data/watch_order_decisions.json to a separate copy.', '',
           f"Reviewed {summary['reviewed_groups']} groups with {summary['decisions']} title decisions. Cycle-blocked titles: {len(before)} before, {len(after)} after.",
           f"Default starting candidates: {summary['starting_candidates_before']} before, {summary['starting_candidates_after']} after.", '',
           'Required prerequisites are conservative recommendation gates. Optional context can help a viewer but does not block a result. Unreviewed dependencies retain the prior conservative rules; release date alone never automatically removes an edge.', '',
           'A change in an affected title’s source prerequisite set fails closed and requires review. Unknown relationships, content filters, recap exclusion, completion checks, and the franchise cap remain active.', '']
    for group in policy['groups']:
        lines += ['## '+group['title'],'', 'Suggested entry points: '+', '.join(f'[{k}](https://myanimelist.net/anime/{k.split(":")[1]})' for k in group['entry_points'])+'.','']
        for d in group['decisions']:
            lines += [f"- **{d['title'] or d['anime_id']} ({d['anime_id']})**: {d['rationale']}",
                      '  Required: '+(', '.join(d['required_prerequisites']) or 'none')+'. Optional context: '+', '.join(d['optional_context'])+'.']
        links=sorted({e['mal_url'] for d in group['decisions'] for e in d['evidence']} |
                     {u for d in group['decisions'] for u in d['additional_sources']})
        lines += ['', 'Evidence: '+', '.join(f'[source {i+1}]({url})' for i,url in enumerate(links))+'.', '']
    lines += ['## Validation limits','',
              'Resolving graph cycles does not prove that every watch-order choice or recommendation is ideal. The untouched source graph still contains the original 18 cycle groups; only the reviewed recommendation graph is acyclic.',
              'Human relevance ratings are not filled in by the assistant. Use the separate review packet to evaluate tone, pacing, genre fit, and request compliance.', '']
    (ROOT/'evaluation/WATCH_ORDER_REVIEW.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in {'formerly_blocked_ids','reviewed_entry_points'}},indent=2))


if __name__=='__main__':main()
