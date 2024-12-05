import networkx as nx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack

def build_graph(data, similarity_matrix, threshold=0.2):
    graph = nx.Graph()
    
    for i, anime in data.iterrows():
        graph.add_node(i, name=anime['name_english'])
    
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            if similarity_matrix[i, j] > threshold:
                graph.add_edge(i, j, weight=similarity_matrix[i, j])
    
    return graph

def get_recommendations(graph, anime_title, data, indices, original_scores, top_n=10):
    if anime_title not in indices:
        return f"'{anime_title}' not found in the dataset."
    
    idx = indices[anime_title]
    neighbors = list(graph.neighbors(idx))
    
    if not neighbors:
        return []

    similarity_scores = [(i, graph.edges[idx, i]['weight']) for i in neighbors]
    sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    if len(sorted_scores) < top_n:
        top_n = len(sorted_scores)
    
    top_scores = sorted_scores[:top_n]
    
    recommended_anime = []
    for i, _ in top_scores:
        original_score = original_scores[i]
        recommended_anime.append({
            'name_english': data['name_english'].iloc[i],
            'img_url': data['img_url'].iloc[i],
            'genres': data['genres'].iloc[i],
            'score': original_score,
            'year': data['start_date'].iloc[i].year if pd.notna(data['start_date'].iloc[i]) else 'Unknown'
        })
    
    return recommended_anime[:top_n]

# Example usage
if __name__ == "__main__":
    # Load the dataset
    data = pd.read_json('C:/Users/trentford/source/repos/YAMWebForm/YAMWebForm/cleaned_anime_data.json')

    # Ensure 'start_date' is in datetime format
    data['start_date'] = pd.to_datetime(data['start_date'], errors='coerce')

    # Initialize the hashmap - moved after cosine similarity calculation
    try:
        synopsis_data = pd.read_json('C:/Users/trentford/source/repos/YAMWebForm/YAMWebForm/synopsis_keywords.json')
        synopsis_data = synopsis_data[['name_english', 'synopsis_keywords']]
    except FileNotFoundError:
        raise FileNotFoundError("The synopsis_keywords.json file is missing.")

    data = data.merge(synopsis_data, on='name_english', how='left')
    data = data[['name_english', 'score', 'ranked', 'popularity', 'members', 'genres', 'type_of', 'studios', 'start_date', 'end_date', 'synopsis_keywords', 'img_url']]
    data[['score', 'ranked', 'popularity', 'members']] = data[['score', 'ranked', 'popularity', 'members']].fillna(0)
    data['synopsis_keywords'] = data['synopsis_keywords'].fillna("")
    
    # Store original scores before scaling and weighting
    original_scores = data['score'].copy()
    
    scaler = MinMaxScaler()
    data[['score', 'ranked', 'popularity', 'members']] = scaler.fit_transform(data[['score', 'ranked', 'popularity', 'members']])
    NUMERICAL_WEIGHT = 0.5
    data['score'] *= NUMERICAL_WEIGHT
    data['members'] *= NUMERICAL_WEIGHT
    TYPE_WEIGHT = 1
    SYNOPSIS_WEIGHT = 2
    data = data[~data['genres'].apply(lambda genres: 'hentai' in genres if genres else False)]

    def combine_features(row):
        genres = " ".join(row['genres']) if row['genres'] else ""
        type_of = row['type_of'].lower().replace(" ", "") if row['type_of'] else ""
        synopsis = row['synopsis_keywords'] if pd.notna(row['synopsis_keywords']) and row['synopsis_keywords'].strip() else ""
        return f"{genres} {type_of} {synopsis}"

    data['combined_features'] = data.apply(combine_features, axis=1)
    data['combined_features'] = data['combined_features'].apply(lambda x: x if x.strip() else "empty_feature")
    data = data[data['combined_features'] != "empty_feature"]
    data = data.reset_index(drop=True)
    vectorizer = TfidfVectorizer(stop_words='english')
    text_features = vectorizer.fit_transform(data['combined_features'])
    numerical_features = data[['score', 'members']].values
    final_features = hstack([text_features, numerical_features])
    cosine_sim = cosine_similarity(final_features)
    indices = pd.Series(data.index, index=data['name_english']).to_dict()
    graph = build_graph(data, cosine_sim, threshold=0.2)

    test_titles = ['86 Eighty-Six']
    for title in test_titles:
        print(f"\nRecommendations for {title}:")
        recommendations = get_recommendations(graph, title, data, indices, original_scores, top_n=10)
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['name_english']} - {rec['img_url']} - {rec['genres']} - {rec['score']} - {rec['year']}")
        else:
            print("No recommendations found.")