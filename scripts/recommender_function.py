import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack

# load the dataset
data = pd.read_json('data/cleaned_anime_data.json')

# Load the filtered synopsis keywords
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

# Vectorize the combined features
vectorizer = TfidfVectorizer(stop_words='english')
text_features = vectorizer.fit_transform(data['combined_features'])

# Combine text and numerical features
numerical_features = data[['score', 'members']].values
final_features = hstack([text_features, numerical_features])

# Compute the cosine similarity
cosine_sim = cosine_similarity(final_features)

# Create a reverse lookup dictionary for the anime titles
indices = pd.Series(data.index, index=data['name_english']).to_dict()

# Create a function to get recommendations
def get_recommendations(title, similarity_matrix, data, top_n=10):
    if title not in indices:
        return f"'{title}' not found in the dataset."
    
    # Get the index of the anime
    idx = indices[title]

    # Get the similarity scores
    similarity_scores = list(enumerate(similarity_matrix[idx]))

    # Sort the scores
    sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Get the top n recommendations excluding the anime itself
    top_scores = sorted_scores[1:top_n+1]

    # Get the anime titles
    # Get the anime titles and remove duplicates
    recommended_anime = []
    seen = set()
    for i, _ in top_scores:
        anime_name = data['name_english'][i]
        if anime_name not in seen:
            recommended_anime.append(anime_name)
            seen.add(anime_name)
    # Return the top n recommendations
    return recommended_anime

# Get recommendations for a given anime
anime_title = 'Jujutsu Kaisen'
recommendations = get_recommendations(anime_title, cosine_sim, data, top_n=10)
print(f"Recommendations for {anime_title}: {recommendations}")

anime_title = 'Naruto Shippuden'
recommendations = get_recommendations(anime_title, cosine_sim, data, top_n=10)
print(f"Recommendations for {anime_title}: {recommendations}")

anime_title = 'Demon Slayer: Kimetsu no Yaiba'
recommendations = get_recommendations(anime_title, cosine_sim, data, top_n=10)
print(f"Recommendations for {anime_title}: {recommendations}")

anime_title = 'Your Lie in April'
recommendations = get_recommendations(anime_title, cosine_sim, data, top_n=10)
print(f"Recommendations for {anime_title}: {recommendations}")

anime_title = 'Mob Psycho 100'
recommendations = get_recommendations(anime_title, cosine_sim, data, top_n=10)
print(f"Recommendations for {anime_title}: {recommendations}")
