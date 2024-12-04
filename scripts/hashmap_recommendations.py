# hashmap_recommendations.py
import pandas as pd

def build_hashmap(data):
    hashmap = {}
    for i, anime in data.iterrows():
        hashmap[anime['name_english']] = {
            'index': i  # Just store index for cosine_sim lookup
        }
    return hashmap

def get_recommendations(hashmap, anime_title, data, cosine_sim, top_n=10):
    if anime_title not in hashmap:
        return f"'{anime_title}' not found in the dataset."
    
    idx = hashmap[anime_title]['index']
    similarity_scores = list(enumerate(cosine_sim[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    
    recommendations = []
    seen = set()
    for i, _ in similarity_scores:
        anime_name = data['name_english'].iloc[i]
        if anime_name not in seen:
            recommendations.append(anime_name)
            seen.add(anime_name)
    
    return recommendations