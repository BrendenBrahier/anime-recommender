import pandas as pd

# load the dataset
data = pd.read_json('data/cleaned_anime_data.json')

# select relevant columns
data = data[['name_english', 'score', 'ranked', 'popularity', 'members', 'genres', 'type_of', 'studios', 'start_date', 'end_date']]

# display the first few rows
print(data.head())