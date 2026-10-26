"""Actual recommender entry point: lazy loading, current data, request filters."""
import os
from pathlib import Path
from functools import lru_cache
try:
    from .recommendation_engine import Recommender
except ImportError:
    from recommendation_engine import Recommender

@lru_cache(maxsize=1)
def get_engine():
    directory=os.environ.get('ANIME_DATA_DIR',str(Path(__file__).resolve().parents[1]/'data/current'))
    return Recommender.from_directory(directory)

def recommend(request,profile=None):
    return get_engine().recommend(request,profile)

def get_combined_recommendations(title,method='filtered',top_n=10,cosine_sim=None,**options):
    if method!='filtered' or cosine_sim is not None:
        raise ValueError('Legacy graph/hashmap dispatch is retired here; use filtered or recommend(request, profile)')
    engine=get_engine()
    matches=[r['anime_id'] for r in engine.catalog if title in {r['anime_id'],r.get('name'),r.get('name_english')}]
    if len(matches)!=1:raise ValueError('Title is missing or ambiguous; supply a stable anime_id')
    return engine.recommend(dict(options,likes=matches,limit=top_n))['results']

if __name__=='__main__':
    import json
    print(json.dumps(recommend({'likes':['mal:1'],'limit':5}),ensure_ascii=True,indent=2))
