import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
from graph_recommendations import build_graph, get_recommendations as get_graph_recommendations
from hashmap_recommendations import build_hashmap, get_recommendations as get_hashmap_recommendations


# load the dataset
data = pd.read_json('data/cleaned_anime_data.json')

# initialize the graph and hashmap - moved after cosine similarity calculation
try:
    synopsis_data = pd.read_json('data/synopsis_keywords.json')
    # Ensure it only contains `name_english` and `synopsis_keywords`
    synopsis_data = synopsis_data[['name_english', 'synopsis_keywords']]
except FileNotFoundError:
    raise FileNotFoundError("The synopsis_keywords.json file is missing.")

# Merge the synopsis keywords into the main dataset
data = data.merge(synopsis_data, on='name_english', how='left')

# Select relevant columns
data = data[['name_english', 'score', 'ranked', 'popularity', 'members', 'genres', 'type_of', 'studios', 'start_date', 'end_date', 'synopsis_keywords']]

# Fill Missing values for numerical columns
data[['score', 'ranked', 'popularity', 'members']] = data[['score', 'ranked', 'popularity', 'members']].fillna(0)
# Fill missing `synopsis_keywords` with an empty string
data['synopsis_keywords'] = data['synopsis_keywords'].fillna("")

# Normalize numerical columns
scaler = MinMaxScaler()
data[['score', 'ranked', 'popularity', 'members']] = scaler.fit_transform(data[['score', 'ranked', 'popularity', 'members']])

# Apply weights to numerical features
NUMERICAL_WEIGHT = 0.5  # Scale numerical weight
data['score'] *= NUMERICAL_WEIGHT
data['members'] *= NUMERICAL_WEIGHT

# Set weight for genres
# GENRES_WEIGHT = 3        # Emphasize genres significantly
TYPE_WEIGHT = 1          # Moderate influence from type_of
SYNOPSIS_WEIGHT = 2      # Moderate contribution from synopsis keywords

data = data[~data['genres'].apply(lambda genres: 'hentai' in genres if genres else False)]
# Combine relevant features into a single column
def combine_features(row):
    genres = " ".join(row['genres']) if row['genres'] else ""
    type_of = row['type_of'].lower().replace(" ", "") if row['type_of'] else ""
    synopsis = row['synopsis_keywords'] if pd.notna(row['synopsis_keywords']) and row['synopsis_keywords'].strip() else ""
    return f"{genres} {type_of} {synopsis}"

# Update the combined features column
data['combined_features'] = data.apply(combine_features, axis=1)

# Check for empty combined features
data['combined_features'] = data['combined_features'].apply(lambda x: x if x.strip() else "empty_feature")

# Optional: Remove rows with no meaningful combined features
data = data[data['combined_features'] != "empty_feature"]
data = data.reset_index(drop=True)  # Reset index to avoid gaps

# Vectorize the combined features
vectorizer = TfidfVectorizer(stop_words='english')
text_features = vectorizer.fit_transform(data['combined_features'])

# Combine text and numerical features
numerical_features = data[['score', 'members']].values
final_features = hstack([text_features, numerical_features])

# Compute the cosine similarity
cosine_sim = cosine_similarity(final_features)


# Create a function to get recommendations
# Create indices dictionary for quick lookups
indices = pd.Series(data.index, index=data['name_english']).to_dict()

def get_cosine_recommendations(title, similarity_matrix, data, top_n=10):
    """Get recommendations using cosine similarity"""
    if title not in indices:
        return f"'{title}' not found in the dataset."
    
    idx = indices[title]
    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    similarity_scores = similarity_scores[1:top_n+1]
    anime_indices = [i[0] for i in similarity_scores]
    return data['name_english'].iloc[anime_indices].tolist()
    
def get_combined_recommendations(title, method='hybrid', top_n=10, cosine_sim=None):
    if title not in indices:
        return f"'{title}' not found in the dataset."

    if method == 'cosine':
        return get_cosine_recommendations(title, cosine_sim, data, top_n)
    elif method == 'graph':
        return get_graph_recommendations(graph, title, data, indices, top_n)
    elif method == 'hashmap':
        return get_hashmap_recommendations(hashmap, title, data, cosine_sim, top_n)
    elif method == 'hybrid':
        cosine_recs = set(get_cosine_recommendations(title, cosine_sim, data, top_n))
        graph_recs = set(get_graph_recommendations(graph, title, data, indices, top_n))
        hashmap_recs = set(get_hashmap_recommendations(hashmap, title, data, cosine_sim, top_n))
        
        final_recs = []
        common_recs = cosine_recs.intersection(graph_recs, hashmap_recs)
        final_recs.extend(list(common_recs))
        
        remaining = list((cosine_recs | graph_recs | hashmap_recs) - common_recs)
        final_recs.extend(remaining[:top_n - len(final_recs)])
        
        return final_recs[:top_n]
    else:
        raise ValueError("Invalid method. Use 'cosine', 'graph', 'hashmap', or 'hybrid'")

def evaluate_recommendations(recommendations, data):
    if not recommendations:
        return {
            'coverage': 0,
            'diversity': 0,
            'relevance': 0
        }
    
    coverage = len(set(recommendations)) / len(data)
    diversity = len(set(recommendations)) / len(recommendations)
    relevance = sum([1 for rec in recommendations if rec in data['name_english'].values]) / len(recommendations)
    
    return {
        'coverage': coverage,
        'diversity': diversity,
        'relevance': relevance
    }
# Initialize the graph with the computed cosine similarity
graph = build_graph(data, cosine_sim, threshold=0.2)
hashmap = build_hashmap(data)

# Example usage
if __name__ == "__main__":
    test_titles = [
        'Your Lie in April',
    ]
    
    methods = ['cosine', 'graph', 'hashmap', 'hybrid']
    
    for title in test_titles:
        print(f"\nRecommendations for {title}:")
        for method in methods:
            recommendations = get_combined_recommendations(title, method=method, cosine_sim=cosine_sim)
            print(f"\n{method.upper()} method:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
            
            metrics = evaluate_recommendations(recommendations, data)
            print(f"Metrics: {metrics}")