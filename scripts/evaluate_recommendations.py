"""Offline development benchmark. Never imports the legacy all-pairs graph module."""
from __future__ import annotations
import argparse
import hashlib
import html
import itertools
import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import sklearn
import scipy
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import MinMaxScaler, normalize, MultiLabelBinarizer

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def violations(row, case):
    """Independent row-level audit; missing constrained metadata fails closed."""
    errors=[]
    f=case['filters']
    if row['anime_id'] in case['likes']+case['dislikes']+case['watched']: errors.append('already_seen_or_disliked')
    if not row.get('recommendation_eligible'): errors.append('ineligible_or_upcoming')
    if row.get('rating')=='Rx - Hentai' or 'hentai' in row.get('genres',[]): errors.append('explicit_content')
    if f.get('formats') and row.get('type_of') not in f['formats']: errors.append('format')
    if f.get('finished') and row.get('status')!='FINISHED': errors.append('not_finished_or_unknown')
    for key,field,op in [('year_min','year',lambda x,y:x<y),('year_max','year',lambda x,y:x>y),('max_episodes','total_episodes',lambda x,y:x>y)]:
        if key in f and (row.get(field) is None or op(row[field],f[key])): errors.append(key+'_or_unknown')
    if set(f.get('excluded_categories',[])) & set(row.get('genres',[])): errors.append('excluded_category')
    if f.get('excluded_categories') and not row.get('genres'): errors.append('unknown_categories')
    return errors

def eligible_mask(frame, case):
    f=case['filters']
    mask=frame.recommendation_eligible.eq(True) & ~frame.anime_id.isin(case['likes']+case['dislikes']+case['watched'])
    mask &= frame.rating.ne('Rx - Hentai') & ~frame.genres.map(lambda x:'hentai' in x)
    if 'formats' in f: mask &= frame.type_of.isin(f['formats'])
    if f.get('finished'): mask &= frame.status.eq('FINISHED')
    if 'year_min' in f: mask &= frame.year.ge(f['year_min'])
    if 'year_max' in f: mask &= frame.year.le(f['year_max'])
    if 'max_episodes' in f: mask &= frame.total_episodes.notna() & frame.total_episodes.le(f['max_episodes'])
    if f.get('excluded_categories'): mask &= frame.genres.map(bool) & ~frame.genres.map(lambda g:bool(set(g)&set(f['excluded_categories'])))
    return mask.to_numpy()

def legacy_features(compat, keywords):
    """Frozen pre-filter cosine features/scaling from the recommender evaluated in PR #34."""
    frame=pd.DataFrame(compat)
    numeric=MinMaxScaler().fit_transform(frame[['score','members']].fillna(0))*.5
    keep=~frame.genres.map(lambda g:'hentai' in g if g else False)
    frame=frame.loc[keep].reset_index(drop=True)
    documents=[' '.join(r['genres'] or [])+' '+(r['type_of'] or '').lower().replace(' ','')+' '+keywords.get(r['anime_id'],'') for r in frame.to_dict('records')]
    # Current export always has a format or a category; do not silently change row mapping.
    assert all(t.strip() for t in documents)
    x=TfidfVectorizer(stop_words='english').fit_transform(documents)
    return frame, normalize(hstack([x,numeric[keep]],format='csr'))

def diversity(rows):
    pairs=list(itertools.combinations(rows,2))
    if not pairs: return None
    def distance(a,b):
        x,y=set(a.get('genres',[])),set(b.get('genres',[]))
        return 1-len(x&y)/len(x|y) if x|y else None
    values=[v for a,b in pairs if (v:=distance(a,b)) is not None]
    return float(np.mean(values)) if values else None

def run(data, cases):
    catalog=read(data/'catalog.json'); frame=pd.DataFrame(catalog)
    lookup={r['anime_id']:r for r in catalog}; positions={r['anime_id']:i for i,r in enumerate(catalog)}
    keywords={r['anime_id']:r['synopsis_keywords'] for r in read(data/'synopsis_keywords.json')}
    old,old_x=legacy_features(read(data/'cleaned_anime_data.json'),keywords)
    old_ids=old.anime_id.tolist(); old_pos={v:i for i,v in enumerate(old_ids)}
    print('Fitting synopsis topics on',len(catalog),'titles',flush=True)
    vectorizer=TfidfVectorizer(stop_words='english',min_df=3,max_df=.8,max_features=30000,ngram_range=(1,2),dtype=np.float32)
    text=vectorizer.fit_transform(frame.synopsis.fillna(''))
    svd=TruncatedSVD(n_components=64,n_iter=5,random_state=42)
    semantic=normalize(svd.fit_transform(text))
    mlb=MultiLabelBinarizer(sparse_output=True)
    genres=normalize(mlb.fit_transform(frame.genres).astype(np.float32))
    classes={g:i for i,g in enumerate(mlb.classes_)}
    # Shrink MAL ratings toward the catalog mean; unknown counts provide no boost.
    prior=float(frame.mal_score.mean()); votes=frame.mal_scored_by.fillna(0).to_numpy()
    quality=((votes*frame.mal_score.fillna(prior).to_numpy()+10000*prior)/(votes+10000))/10
    runs=[]
    for case in cases:
        likes=[positions[i] for i in case['likes']]; dislikes=[positions[i] for i in case['dislikes']]
        qtext=vectorizer.transform([case['query']]); qsemantic=normalize(svd.transform(qtext))
        if likes:
            qtext=normalize(.5*qtext+.5*csr_matrix(text[likes].mean(axis=0)))
            qsemantic=normalize(.5*qsemantic+.5*semantic[likes].mean(axis=0,keepdims=True))
        qgenre=np.zeros((1,len(classes)),dtype=np.float32)
        for g in case['preferred_categories']:
            if g in classes:qgenre[0,classes[g]]=1
        if likes:qgenre+=np.asarray(genres[likes].mean(axis=0))
        qgenre=normalize(qgenre)
        scores=.35*(text@qtext.T).toarray().ravel()
        scores+=.30*(semantic@qsemantic.T).ravel()+.25*np.asarray(genres@qgenre.T).ravel()+.10*quality
        if dislikes:scores-=.15*np.maximum(semantic@semantic[dislikes].mean(axis=0),0)
        valid=np.flatnonzero(eligible_mask(frame,case))
        pool=sorted(valid,key=lambda i:(-float(scores[i]),catalog[i]['anime_id']))[:150]
        selected=[]
        while pool and len(selected)<5:
            def mmr(i):
                penalty=max((max(0,float(semantic[i]@semantic[j])) for j in selected),default=0)
                return float(scores[i])-.10*penalty
            best=max(pool,key=mmr); selected.append(best);pool.remove(best)
        choices={'hybrid':[catalog[i]['anime_id'] for i in selected]}
        if case['likes'] and case['likes'][0] in old_pos:
            ix=old_pos[case['likes'][0]]; sim=(old_x@old_x[ix].T).toarray().ravel()
            # Stable tie order and seed exclusion, equivalent for non-identical seed vectors.
            ordered=np.argsort(-sim,kind='stable'); choices['legacy_cosine']=[old_ids[i] for i in ordered if i!=ix][:5]
            # Control isolates the benefit of filtering from changes in ranking.
            choices['legacy_filtered']=[old_ids[i] for i in ordered if i!=ix and not violations(lookup[old_ids[i]],case)][:5]
        else:choices.update(legacy_cosine=[],legacy_filtered=[])
        for model,ids in choices.items():
            rows=[lookup[i] for i in ids]
            results=[{'rank':j+1,'anime_id':r['anime_id'],'title':r['name_english'],'year':r['year'],'format':r['type_of'],'episodes':r['total_episodes'],'status':r['status'],'categories':r['genres'],'violations':violations(r,case)} for j,r in enumerate(rows)]
            runs.append({'case_id':case['id'],'model':model,'supported':model=='hybrid' or bool(case['likes']), 'results':results,'category_diversity':diversity(rows),'preferred_category_overlap':float(np.mean([len(set(r['genres'])&set(case['preferred_categories']))/len(case['preferred_categories']) for r in rows])) if rows else None})
    return runs, {'catalog_entries':len(catalog),'catalog_sha256':hashlib.sha256((data/'catalog.json').read_bytes()).hexdigest(),'cases_sha256':hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest(),'sklearn':sklearn.__version__,'scipy':scipy.__version__,'numpy':np.__version__,'svd_explained_variance':float(svd.explained_variance_ratio_.sum()),'random_seed':42}

def summarize(runs):
    summary={}
    for model in sorted({r['model'] for r in runs}):
        subset=[r for r in runs if r['model']==model]; supported=[r for r in subset if r['supported']]
        results=[x for r in supported for x in r['results']]
        diversities=[r['category_diversity'] for r in supported if r['category_diversity'] is not None]
        summary[model]={'requests':len(subset),'supported':len(supported),'returned':len(results),'violating_results':sum(bool(x['violations']) for x in results),'violation_rate':sum(bool(x['violations']) for x in results)/len(results) if results else None,'slot_fill_rate':len(results)/(5*len(supported)) if supported else None,'category_diversity':float(np.mean(diversities)) if diversities else None,'unique_titles':len({x['anime_id'] for x in results})}
    return summary

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--data',type=Path,default=ROOT/'data/current'); parser.add_argument('--output',type=Path,default=ROOT/'evaluation/results'); args=parser.parse_args()
    cases=read(ROOT/'evaluation/cases.json'); runs,manifest=run(args.data,cases)
    manifest['created_utc']=datetime.now(timezone.utc).isoformat()
    args.output.mkdir(exist_ok=True,parents=True)
    result={'manifest':manifest,'summary':summarize(runs),'runs':runs}
    (args.output/'benchmark.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    # Blind candidate-level review: model and rank hidden; de-duplicate shared candidates.
    rng=np.random.default_rng(42); by_id={r['anime_id']:r for r in read(args.data/'catalog.json')}; review=[]
    for case in cases:
        ids=sorted({x['anime_id'] for r in runs if r['case_id']==case['id'] and r['model']!='legacy_filtered' for x in r['results']});rng.shuffle(ids)
        for i in ids:
            row=by_id[i]
            review.append({'case_id':case['id'],'anime_id':i,'title':row['name_english'],'prompt':case['prompt'],'synopsis':row.get('synopsis'),'categories':row['genres'],'year':row['year'],'format':row['type_of'],'episodes':row['total_episodes'],'status':row['status'],'grade':None,'reason':'','reviewer':''})
    (args.output/'review_queue.json').write_text(json.dumps(review,indent=2,ensure_ascii=False),encoding='utf-8')
    cards=['<!doctype html><meta charset="utf-8"><title>Anime recommendation review</title><style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:20px}article{border-bottom:1px solid #ccc;padding:20px 0}small{color:#555}</style><h1>Blind recommendation review</h1><p>Grade 0: unrelated; 1: weak; 2: plausible; 3: strong. Judge topical fit separately from hard constraints. Unknown: leave blank. These are development cases, not held-out test data. Model identity and rank are hidden.</p>']
    for r in review:
        cards.append('<article><small>'+html.escape(r['case_id']+' / '+r['anime_id'])+'</small><h2>'+html.escape(r['title'])+'</h2><b>'+html.escape(r['prompt'])+'</b><p>'+html.escape(str(r['year'])+' | '+str(r['format'])+' | '+str(r['episodes'])+' episodes | '+', '.join(r['categories']))+'</p><p>'+html.escape(r['synopsis'] or 'No synopsis available')+'</p></article>')
    (args.output/'review.html').write_text('\n'.join(cards),encoding='utf-8')
    print(json.dumps(result['summary'],indent=2),flush=True)

if __name__=='__main__':main()
