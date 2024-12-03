import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler

# load the dataset
data = pd.read_json('data/cleaned_anime_data.json')

# select relevant columns
data = data[['name_english', 'score', 'ranked', 'popularity', 'members', 'genres', 'type_of', 'studios', 'start_date', 'end_date']]

# Fill Missing values with numerical columns
data[['score', 'ranked', 'popularity', 'members']] = data[['score', 'ranked', 'popularity', 'members']].fillna(0)
# Normalize numerical columns
scaler = MinMaxScaler()
data[['score', 'ranked', 'popularity', 'members']] = scaler.fit_transform(data[['score', 'ranked', 'popularity', 'members']])



# Combine relevant columns into a single column
def combine_features(row):
    genres = " ".join(row['genres']) if row['genres'] else ""
    studios = row['studios'].lower().replace(" ", "") if row['studios'] else ""
    type_of = row['type_of'].lower().replace(" ", "") if row['type_of'] else ""
    return f"{genres} {studios} {type_of}"

data['combined_features'] = data.apply(combine_features, axis=1)

# check the combined features
print(data[['name_english', 'combined_features']].head())
