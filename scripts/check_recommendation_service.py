"""Run existing requests against the actual service; preserve prior benchmark and labels."""
import json
from pathlib import Path
from collections import Counter
from recommendation_engine import Recommender
from evaluate_recommendations import violations

ROOT=Path(__file__).resolve().parents[1]
def main():
    cases=json.loads((ROOT/'evaluation/cases.json').read_text(encoding='utf-8'))
    engine=Recommender.from_directory()
    catalog={r['anime_id']:r for r in engine.catalog}
    runs=[];problems=[]
    for case in cases:
        request={k:case[k] for k in ['likes','dislikes','watched','query','filters']}
        request['limit']=5
        response=engine.recommend(request)
        families=Counter()
        for row in response['results']:
            key=row['anime_id'];relation=engine.relationships[key]
            issues=violations(catalog[key],case)
            # Cases provide likes/watched IDs, but do not declare prerequisite completion.
            if relation['prerequisites']:issues.append('prerequisite_not_completed')
            if not relation['verified_relations']:issues.append('unverified_relationships')
            if relation['recap_status']!='none_detected':issues.append('recap_or_unknown')
            families[relation['franchise_id']]+=1
            if families[relation['franchise_id']]>1:issues.append('franchise_duplicate')
            if issues:problems.append({'case_id':case['id'],'anime_id':key,'issues':issues})
        runs.append({'case_id':case['id'],**response})
    summary={'requests':len(cases),'requested_slots':len(cases)*5,'returned':sum(len(r['results']) for r in runs),'requests_with_five_results':sum(len(r['results'])==5 for r in runs),'violating_results':len(problems),'verified_relationship_catalog_entries':sum(k in catalog and r.get('verified_relations',False) for k,r in engine.relationships.items()),'catalog_entries':len(catalog),'relevance':'Not graded; prior prototype relevance scores do not apply to this service.'}
    result={'summary':summary,'violations':problems,'runs':runs}
    (ROOT/'evaluation/results/service_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if problems:raise SystemExit('Recommendation policy violations detected')

if __name__=='__main__':main()
