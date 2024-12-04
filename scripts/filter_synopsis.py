import pandas as pd
import spacy
import json

# Load spaCy's English model
nlp = spacy.load('en_core_web_sm')

# Function to clean and extract keywords from the synopsis
def extract_keywords(text):
    doc = nlp(text)
    # Keep only nouns, verbs, and adjectives; filter out proper nouns (names) and stopwords
    keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and token.pos_ not in ['PROPN']]
    return " ".join(keywords)

def process_synopsis(data):
    # Process synopsis in batches
    processed_synopsis = []
    for doc in nlp.pipe(data['synopsis'].fillna("").tolist(), batch_size=50, disable=["ner", "parser"]):
        keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and token.pos_ not in ['PROPN']]
        processed_synopsis.append(" ".join(keywords))
    return processed_synopsis

def save_processed_synopsis(input_file, output_file):
    # Load the dataset
    data = pd.read_json(input_file)

    # Process the synopsis
    print("Processing synopsis...")
    data['synopsis_keywords'] = process_synopsis(data)

    # Keep only relevant columns (e.g., name_english and synopsis_keywords)
    processed_data = data[['name_english', 'synopsis_keywords']]

    # Save the processed data
    processed_data.to_json(output_file, orient='records', indent=4)
    print(f"Processed file with synopsis keywords saved to {output_file}")

if __name__ == "__main__":
    input_file = 'data/cleaned_anime_data.json'
    output_file = 'data/synopsis_keywords.json'
    save_processed_synopsis(input_file, output_file)
