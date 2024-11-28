import json
from datetime import datetime

def load_dataset(file_path):
    # load json dataset from file.
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    except Exception as e:
        print(f"Error loading dataset from {file_path}: {e}")
        return []
    
def save_dataset(file_path, dataset):
    # save json dataset to file.
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(dataset, file, indent=4, ensure_ascii=False)
        print(f"Dataset saved to {file_path}")

    except Exception as e:
        print(f"Error saving dataset to {file_path}: {e}")

def handle_missing_fields(data):
    # handle missing field in the dataset.
    for anime in data:
        anime['genres'] = anime.get('genres', ["unknown"])
        anime['img_url'] = anime.get('img_url', "https://example.com/placeholder.jpg")
        name_english = anime.get('name_english')
        name = anime.get('name')
        anime['name_english'] = (name_english or name or "Unknown").strip() if isinstance(name_english or name, str) else "Unknown"

        # Safely handle score
        score = anime.get('score')
        try:
            anime['score'] = round(float(score), 2) if score and score != 'N/A' else None
        except (ValueError, TypeError):
            anime['score'] = None  # Default to None if conversion fails
    
    return data

def standardize_fields(data):
    # standardize the data types and normalize values.
    for anime in data:
        # Convert numerical fields to the proper types
        for field in ['ranked', 'popularity', 'members', 'favorites', 'completed', 'watching', 'total_episodes', "on_hold", "dropped", "plan_to_watch", "total", "scored_10_by", "scored_9_by", "scored_8_by", "scored_7_by", "scored_6_by", "scored_5_by", "scored_4_by", "scored_3_by", "scored_2_by", "scored_1_by"]:
            value = anime.get(field)  # Get the value of the field
            try:
                # If the value is a string, remove commas and convert to int
                anime[field] = int(value.replace(",", "")) if isinstance(value, str) else int(value)
            except (ValueError, TypeError):
                anime[field] = 0  # Default to 0 for invalid or missing values
        
        # Standardize genres to lowercase
        anime['genres'] = [genre.lower() for genre in anime.get('genres', []) if genre]

    return data

def validate_data_ranges(data):
    # validate numerical ranges for the dataset.
    for anime in data:
        if 'score' in anime and anime['score']:
            anime['score'] = max(0.00, min(10.00, anime['score']))
        if 'ranked' in anime and anime['ranked']:
            anime['ranked'] = max(1, anime['ranked'])   
        if 'popularity' in anime and anime['popularity']:
            anime['popularity'] = max(0, anime['popularity'])
        if 'members' in anime and anime['members']:
            anime['members'] = max(0, anime['members'])
        if 'favorites' in anime and anime['favorites']:
            anime['favorites'] = max(0, anime['favorites'])
        if 'completed' in anime and anime['completed']:
            anime['completed'] = max(0, anime['completed'])
        if 'watching' in anime and anime['watching']:
            anime['watching'] = max(0, anime['watching'])
        if 'total_episodes' in anime and anime['total_episodes']:
            anime['total_episodes'] = max(0, anime['total_episodes'])
        if 'on_hold' in anime and anime['on_hold']:
            anime['on_hold'] = max(0, anime['on_hold'])
        if 'dropped' in anime and anime['dropped']:
            anime['dropped'] = max(0, anime['dropped'])
        if 'plan_to_watch' in anime and anime['plan_to_watch']:
            anime['plan_to_watch'] = max(0, anime['plan_to_watch'])
        if 'total' in anime and anime['total']:
            anime['total'] = max(0, anime['total'])
        if 'scored_10_by' in anime and anime['scored_10_by']:
            anime['scored_10_by'] = max(0, anime['scored_10_by'])
        if 'scored_9_by' in anime and anime['scored_9_by']:
            anime['scored_9_by'] = max(0, anime['scored_9_by'])
        if 'scored_8_by' in anime and anime['scored_8_by']:
            anime['scored_8_by'] = max(0, anime['scored_8_by'])
        if 'scored_7_by' in anime and anime['scored_7_by']:
            anime['scored_7_by'] = max(0, anime['scored_7_by'])
        if 'scored_6_by' in anime and anime['scored_6_by']:
            anime['scored_6_by'] = max(0, anime['scored_6_by'])
        if 'scored_5_by' in anime and anime['scored_5_by']:
            anime['scored_5_by'] = max(0, anime['scored_5_by'])
        if 'scored_4_by' in anime and anime['scored_4_by']:
            anime['scored_4_by'] = max(0, anime['scored_4_by'])
        if 'scored_3_by' in anime and anime['scored_3_by']:
            anime['scored_3_by'] = max(0, anime['scored_3_by'])
        if 'scored_2_by' in anime and anime['scored_2_by']:
            anime['scored_2_by'] = max(0, anime['scored_2_by'])
        if 'scored_1_by' in anime and anime['scored_1_by']:
            anime['scored_1_by'] = max(0, anime['scored_1_by'])
        
        
    return data

if __name__ == "__main__":
    input_file = 'data/final_anime_data.json'
    output_file = 'data/cleaned_anime_data.json'

    print ("Loading dataset...")
    dataset = load_dataset(input_file)

    print("Handling missing fields...")
    dataset = handle_missing_fields(dataset)

    print("Standardizing fields...")
    dataset = standardize_fields(dataset)

    print("Validating data ranges...")
    dataset = validate_data_ranges(dataset)

    print("Saving dataset...")
    save_dataset(output_file, dataset)

    print("Data preprocessing completed.")