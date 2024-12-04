import json

def load_dataset(file_path):
    # Load JSON dataset from file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading dataset from {file_path}: {e}")
        return []

def save_titles(file_path, titles):
    # Save titles to a JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(titles, file, indent=4, ensure_ascii=False)
        print(f"Titles saved to {file_path}")
    except Exception as e:
        print(f"Error saving titles to {file_path}: {e}")

def extract_and_alphabatize_titles(data):
    # Extract and alphabetize titles from the dataset
    titles = [anime.get('name_english', 'Unknown') for anime in data if anime.get('name_english')]
    titles.sort(key=lambda title: title.lower())  # Sort case-insensitively
    return titles

if __name__ == "__main__":
    input_file = 'data/final_anime_data.json'
    output_file = 'data/alphabetized_titles.json'

    print("Loading dataset...")
    dataset = load_dataset(input_file)

    if dataset:  # Check if dataset is not empty
        print("Extracting and sorting titles...")
        titles = extract_and_alphabatize_titles(dataset)

        print("Saving alphabetized titles...")
        save_titles(output_file, titles)

        print("Alphabetized titles saved.")
    else:
        print("Dataset is empty or could not be loaded.")


