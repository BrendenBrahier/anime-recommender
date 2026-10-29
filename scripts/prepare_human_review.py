"""Create a local review form with unanswered human ratings; upload nothing."""
import json
from pathlib import Path
from recommendation_engine import Recommender
from enrich_catalog import save

ROOT=Path(__file__).resolve().parents[1]
CASES=['space-1','mystery-1','fantasy-1','romance-1','sports-1','calm-1',
       'thriller-1','music-1','space-2','mystery-3','romance-4','fantasy-5']


def main():
    cases={c['id']:c for c in json.loads((ROOT/'evaluation/cases.json').read_text(encoding='utf-8'))}
    engine=Recommender.from_directory()
    catalog={r['anime_id']:r for r in engine.catalog}
    packet={'schema_version':1,'reviewer':None,'policy_sha256':engine.watch_order_policy_sha256,
            'instructions':'Rate how well each anime fits the fictional request. Leave unknown when you cannot judge. These are not imported personal preferences.',
            'cases':[]}
    for key in CASES:
        case=cases[key]
        request={k:case[k] for k in ['likes','dislikes','watched','query','filters']}
        request['limit']=3
        response=engine.recommend(request)
        results=[]
        for result in response['results']:
            row=catalog[result['anime_id']]
            results.append({'anime_id':row['anime_id'],'title':row.get('name_english') or row['name'],
                            'synopsis':(row.get('synopsis') or '')[:900],
                            'genres':row.get('genres',[]),'year':row.get('year'),'format':row.get('type_of'),
                            'episodes':row.get('total_episodes'),'relevance':None,'issues':[],'notes':''})
        packet['cases'].append({'case_id':key,'prompt':case['prompt'],'request':request,'results':results})
    destination=ROOT/'data/private/human-review'
    save(destination/'blank_review.json',packet)
    template=(ROOT/'scripts/templates/human_review.html').read_text(encoding='utf-8')
    payload=json.dumps(packet,ensure_ascii=True).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    (destination/'review.html').write_text(template.replace('__PAYLOAD__',payload),encoding='utf-8')
    manifest={'schema_version':1,'policy_sha256':packet['policy_sha256'],'case_count':len(packet['cases']),
              'result_count':sum(len(c['results']) for c in packet['cases']),
              'rating_status':'Awaiting human review; no relevance scores have been assigned.',
              'cases':[{'case_id':c['case_id'],'prompt':c['prompt'],
                        'results':[{'anime_id':r['anime_id'],'title':r['title']} for r in c['results']]} for c in packet['cases']]}
    save(ROOT/'evaluation/human_review_manifest.json',manifest)
    print(json.dumps({'form':str(destination/'review.html'),'cases':manifest['case_count'],'recommendations':manifest['result_count']},indent=2))


if __name__=='__main__':main()
