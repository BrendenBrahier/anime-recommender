"""Request-aware sparse recommender; loads the current catalog only on construction."""
from collections import Counter
import json
import hashlib
import math
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from scipy.sparse import csr_matrix
try:
    from .mal_profile import preferences
    from .watch_order import load_policy, apply_policy
except ImportError:
    from mal_profile import preferences
    from watch_order import load_policy, apply_policy

ROOT=Path(__file__).resolve().parents[1]
FORMATS={'tv','movie','ova','ona','special','music','tv_special'}

def validate_request(request):
    if not isinstance(request,dict):raise ValueError('Request must be an object')
    allowed={'likes','dislikes','watched','completed','query','filters','limit','max_per_franchise','allow_sequels','allow_recaps','allow_unknown_relationships','allow_unknown_content'}
    if set(request)-allowed:raise ValueError('Unknown request fields: '+', '.join(sorted(set(request)-allowed)))
    if not isinstance(request.get('query',''),str) or len(request.get('query',''))>2000:raise ValueError('Invalid query')
    for key in ['likes','dislikes','watched','completed']:
        if not isinstance(request.get(key,[]),list) or any(not isinstance(i,str) for i in request.get(key,[])):raise ValueError('Expected a list of stable anime IDs')
    for key,default,max_value in [('limit',10,50),('max_per_franchise',1,5)]:
        value=request.get(key,default)
        if type(value) is not int or not 1<=value<=max_value:raise ValueError('Invalid '+key)
    for key in ['allow_sequels','allow_recaps','allow_unknown_relationships','allow_unknown_content']:
        if key in request and type(request[key]) is not bool:raise ValueError('Expected boolean '+key)
    filters=request.get('filters',{})
    if not isinstance(filters,dict):raise ValueError('filters must be an object')
    if set(filters)-{'formats','year_min','year_max','max_episodes','finished','excluded_categories','allowed_ratings'}:raise ValueError('Unknown filter')
    for key in ['formats','excluded_categories','allowed_ratings']:
        if key in filters and (not isinstance(filters[key],list) or not filters[key] or any(not isinstance(x,str) for x in filters[key])):raise ValueError('Expected nonempty string list for '+key)
    if set(filters.get('formats',[]))-FORMATS:raise ValueError('Unknown format')
    for key in ['year_min','year_max','max_episodes']:
        if key in filters and (type(filters[key]) is not int or filters[key]<=0):raise ValueError('Invalid '+key)
    if filters.get('year_min',0)>filters.get('year_max',9999):raise ValueError('Invalid year range')
    if 'finished' in filters and type(filters['finished']) is not bool:raise ValueError('finished must be boolean')

def content_reasons(row, filters, allow_unknown_content=False):
    reasons=[]
    if not row.get('recommendation_eligible'):reasons.append('ineligible')
    genres=set(row.get('genres') or [])
    if row.get('rating')=='Rx - Hentai' or 'hentai' in genres:reasons.append('explicit_content')
    if not row.get('rating') and not allow_unknown_content:reasons.append('unknown_content_rating')
    if filters.get('formats') and row.get('type_of') not in filters['formats']:reasons.append('format')
    if filters.get('allowed_ratings') and row.get('rating') not in filters['allowed_ratings']:reasons.append('content_rating')
    if filters.get('finished') and row.get('status')!='FINISHED':reasons.append('not_finished')
    for key,field,op in [('year_min','year',lambda v,b:v<b),('year_max','year',lambda v,b:v>b),('max_episodes','total_episodes',lambda v,b:v>b)]:
        if key in filters:
            value=row.get(field)
            if value is None or not isinstance(value,(int,float)) or not math.isfinite(value) or op(value,filters[key]):reasons.append(key)
    if filters.get('excluded_categories') and (not genres or genres&set(filters['excluded_categories'])):reasons.append('excluded_or_unknown_categories')
    return reasons

def relationship_reasons(key, records, completed, allow_sequels=True, allow_recaps=False, allow_unknown=False):
    row=records.get(key)
    if not row:return [] if allow_unknown else ['unknown_relationships']
    reasons=[]
    if not row.get('verified_relations') and not allow_unknown:reasons.append('unknown_relationships')
    recap=row.get('recap_status','unknown')
    if not allow_recaps and recap in {'confirmed','suspected'}:reasons.append('recap')
    if not allow_recaps and recap=='unknown' and not allow_unknown:reasons.append('unknown_recap_status')
    prequels=row.get('prerequisites',[])
    if prequels and not allow_sequels:reasons.append('sequels_disabled')
    # Completion of every direct predecessor is required. A mere high score, liked
    # title, watching status, or planned title never establishes completion.
    if any(p not in completed for p in prequels):reasons.append('unwatched_prerequisite')
    # A cycle is contradictory evidence even when both IDs appear completed.
    def cyclic(current,path):
        if current in path or len(path)>=100:return True
        return any(cyclic(p,path|{current}) for p in records.get(current,{}).get('prerequisites',[]))
    if cyclic(key,set()):reasons.append('cyclic_prerequisites')
    return reasons

class Recommender:
    def __init__(self,catalog,relationships,watch_order_policy=None):
        self.catalog=catalog;self.relationships=relationships.get('records',{})
        self.source_relationships=self.relationships
        if watch_order_policy is not None:
            self.relationships=apply_policy(self.source_relationships,watch_order_policy)
        self.positions={r['anime_id']:i for i,r in enumerate(catalog)}
        if len(self.positions)!=len(catalog):raise ValueError('Duplicate catalog IDs')
        self.vectorizer=TfidfVectorizer(stop_words='english',max_features=40000,ngram_range=(1,2),dtype=np.float32)
        documents=[' '.join(r.get('genres') or [])+' '+(r.get('synopsis') or '') for r in catalog]
        self.features=self.vectorizer.fit_transform(documents)

    @classmethod
    def from_directory(cls,data=None):
        data=Path(data or ROOT/'data/current')
        with (data/'catalog.json').open(encoding='utf-8') as f:catalog=json.load(f)
        # Missing evidence is represented explicitly, never silently treated as no prerequisites.
        path=data/'relationships.json'
        relationships=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'records':{}}
        expected=relationships.get('catalog_sha256')
        if expected and expected!=hashlib.sha256((data/'catalog.json').read_bytes()).hexdigest():
            raise ValueError('Catalog changed; rebuild relationships with scripts/build_relationships.py')
        policy,policy_hash=load_policy()
        engine=cls(catalog,relationships,watch_order_policy=policy)
        engine.watch_order_policy_sha256=policy_hash
        return engine

    def recommend(self,request,profile=None):
        validate_request(request)
        pref=preferences(profile or {'entries':[]})
        likes=dict(pref['likes']);likes.update({i:1. for i in request.get('likes',[])})
        dislikes=dict(pref['dislikes']);dislikes.update({i:1. for i in request.get('dislikes',[])})
        for i in dislikes:likes.pop(i,None)
        completed=pref['completed']|set(request.get('completed',[]))
        excluded=pref['exclude']|set(request.get('watched',[]))|completed|set(likes)|set(dislikes)
        user_ids=set(likes)|set(dislikes)|excluded
        unknown_ids=sorted(user_ids-self.positions.keys())
        positive=[(self.positions[k],w) for k,w in likes.items() if k in self.positions]
        query=self.vectorizer.transform([request.get('query','')])
        if positive:
            indices,weights=zip(*positive)
            weights=np.asarray(weights,dtype=np.float32);weights/=weights.sum()
            seed=csr_matrix(weights.reshape(1,-1))@self.features[list(indices)]
            query=normalize(.5*query+.5*seed) if query.nnz else normalize(seed)
        if not query.nnz:
            return {'results':[],'warnings':['Add a liked title or a description; no usable positive preferences were found.'],'unknown_profile_or_request_ids':unknown_ids,'excluded_counts':{}}
        scores=(self.features@query.T).toarray().ravel()
        negative=[(self.positions[k],w) for k,w in dislikes.items() if k in self.positions]
        if negative:
            indices,weights=zip(*negative);weights=np.asarray(weights,dtype=np.float32);weights/=weights.sum()
            neg=normalize(csr_matrix(weights.reshape(1,-1))@self.features[list(indices)])
            scores-=.20*(self.features@neg.T).toarray().ravel()
        rejected=Counter();candidates=[]
        for i,row in enumerate(self.catalog):
            key=row['anime_id']; reasons=[]
            if key in excluded:reasons.append('seen_or_disliked')
            reasons+=content_reasons(row,request.get('filters',{}),request.get('allow_unknown_content',False))
            reasons+=relationship_reasons(key,self.relationships,completed,request.get('allow_sequels',True),request.get('allow_recaps',False),request.get('allow_unknown_relationships',False))
            if reasons:rejected.update(reasons);continue
            if scores[i]<=0:rejected['no_positive_match']+=1;continue
            candidates.append(i)
        candidates.sort(key=lambda i:(-float(scores[i]),self.catalog[i]['anime_id']))
        selected=[];families=Counter()
        for i in candidates:
            row=self.catalog[i];key=row['anime_id'];rel=self.relationships.get(key,{})
            family=rel.get('franchise_id',key)
            if families[family]>=request.get('max_per_franchise',1):rejected['franchise_limit']+=1;continue
            families[family]+=1
            selected.append({k:row.get(k) for k in ['anime_id','name_english','img_url','year','type_of','total_episodes','rating','aggregate_score','mal_score']})
            selected[-1].update({'match_score':round(float(scores[i]),6),'franchise_id':family,'relationship_verified':rel.get('verified_relations',False),'recap_status':rel.get('recap_status','unknown'),'prerequisites':rel.get('prerequisites',[]),'recommendation_reason':'Matches the supplied description and/or positively rated titles after request and viewing-order filters.'})
            selected[-1].update({'optional_context':rel.get('optional_context',[]),
                                'watch_order_decision':rel.get('watch_order_decision'),
                                'reviewed_entry_point':rel.get('reviewed_entry_point',False)})
            if len(selected)==request.get('limit',10):break
        warnings=[]
        if len(selected)<request.get('limit',10):warnings.append('Fewer matches passed all filters; constraints were not relaxed.')
        if request.get('allow_unknown_relationships'):warnings.append('Unverified relationships allowed: starting-point and franchise guarantees are limited.')
        if request.get('allow_unknown_content'):warnings.append('Titles with unknown content ratings are allowed.')
        return {'results':selected,'warnings':warnings,'unknown_profile_or_request_ids':unknown_ids,'excluded_counts':dict(rejected)}
