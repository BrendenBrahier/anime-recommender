"""Build a provenance-bearing relationship sidecar from cached MAL-compatible details."""
import argparse
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from enrich_catalog import request, save

ROOT=Path(__file__).resolve().parents[1]
FAMILY={'prequel','sequel','parent story','side story','summary','full story','alternative version','alternative setting','spin-off'}

def build(records, catalog):
    rows={}; parent={}; prereqs={}; recaps=set()
    def find(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[max(a,b)]=min(a,b)
    for record in records:
        item=record.get('response',{}).get('data')
        if not isinstance(item,dict) or not isinstance(item.get('relations'),list):continue
        mid=item.get('mal_id')
        if type(mid) is not int or mid<=0:continue
        key=f'mal:{mid}';find(key)
        relations=[]
        for relation in item['relations']:
            kind=relation.get('relation','').lower().replace('_',' ')
            for entry in relation.get('entry',[]):
                if entry.get('type')!='anime' or type(entry.get('mal_id')) is not int:continue
                target=f"mal:{entry['mal_id']}"
                relations.append({'type':kind,'anime_id':target})
                if kind in FAMILY:union(key,target)
                if kind in {'prequel','parent story'}:prereqs.setdefault(key,set()).add(target)
                if kind in {'sequel','side story'}:prereqs.setdefault(target,set()).add(key)
                if kind=='full story':recaps.add(key)
                if kind=='summary':recaps.add(target)
        synopsis=item.get('synopsis') or ''
        title=item.get('title') or ''
        suspected=bool(re.search(r'\b(?:recap|compilation|soushuuhen|recapitulation)\b',title,re.I) or re.search(r'\b(?:recap|compilation|summary|retelling) (?:of|episode|movie|film)',synopsis,re.I))
        rows[key]={'anime_id':key,'verified_relations':True,'relations':relations,'recap_status':'suspected' if suspected else ('none_detected' if synopsis.strip() else 'unknown'),'source_url':record.get('url'),'retrieved_at':record.get('retrieved_at')}
    for key in set(rows)|set(parent)|set(prereqs)|recaps:
        row=rows.setdefault(key,{'anime_id':key,'verified_relations':False,'relations':[],'recap_status':'unknown'})
        row['franchise_id']=find(key)
        row['prerequisites']=sorted(prereqs.get(key,set()))
        if key in recaps:row['recap_status']='confirmed'
    return {'schema_version':1,'built_utc':datetime.now(timezone.utc).isoformat(),'catalog_entries':len(catalog),'verified_catalog_entries':sum(k in rows and rows[k]['verified_relations'] for k in catalog),'records':rows}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--download',action='store_true');parser.add_argument('--max-fetch',type=int,default=500);args=parser.parse_args()
    catalog={r['anime_id']:r for r in json.loads((ROOT/'data/current/catalog.json').read_text(encoding='utf-8'))}
    cache=ROOT/'data/raw/tenrai'
    if args.download:
        cases=json.loads((ROOT/'evaluation/cases.json').read_text(encoding='utf-8'))
        results=json.loads((ROOT/'evaluation/results/benchmark.json').read_text(encoding='utf-8'))
        seeds={i for c in cases for key in ['likes','dislikes','watched'] for i in c[key]}
        seeds|={x['anime_id'] for run in results['runs'] for x in run['results']}
        popular=sorted((r for r in catalog.values() if r.get('mal_id') and r.get('popularity')),key=lambda r:r['popularity'])[:100]
        seeds|={r['anime_id'] for r in popular}
        pending=sorted(int(k.split(':')[1]) for k in seeds if k.startswith('mal:'));seen=set();fetched=0
        while pending and fetched<args.max_fetch:
            mid=pending.pop(0)
            if mid in seen:continue
            seen.add(mid)
            record=request(f'anime/{mid}/full');fetched+=1
            print(f'Relationship evidence {fetched}: MAL {mid}',flush=True)
            item=record.get('response',{}).get('data') or {}
            if item.get('mal_id')!=mid:continue
            for relation in item.get('relations',[]):
                if relation.get('relation','').lower()=='prequel':
                    pending.extend(e['mal_id'] for e in relation.get('entry',[]) if e.get('type')=='anime' and type(e.get('mal_id')) is int and e['mal_id'] not in seen)
    records=[]
    for path in sorted(cache.glob('anime_*_full.json')):
        record=json.loads(path.read_text(encoding='utf-8'));item=record.get('response',{}).get('data') or {}
        expected=int(path.name.split('_')[1])
        if item.get('mal_id')==expected:records.append(record)
    result=build(records,catalog)
    result['catalog_sha256']=hashlib.sha256((ROOT/'data/current/catalog.json').read_bytes()).hexdigest()
    save(ROOT/'data/current/relationships.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))

if __name__=='__main__':main()
