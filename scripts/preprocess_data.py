import json
import pandas as pd
import ast  # To safely parse genres


def merge_data():
    try:
        # Load the JSON files
        print("Loading ani_data_full.json...")
        with open('data/ani_data_full.json', 'r', encoding='utf-8') as details_file:
            ani_data_full = json.load(details_file)

        print("Loading ani_img.json...")
        with open('data/ani_img.json', 'r', encoding='utf-8') as img_file:
            ani_img = json.load(img_file)

        # Load the preprocessed CSV file
        print("Loading preprocessed_ani_data.csv...")
        preprocessed_csv = pd.read_csv('data/preprocessed_ani_data.csv')

        # Load the new Anime_Data.csv file
        print("Loading Anime_Data.csv...")
        new_csv = pd.read_csv('data/Anime_Data.csv')

        # Convert ani_img.json to a dictionary for quick access
        print("Converting image data to dictionary...")
        img_dic = {entry["name_english"]: entry["img"] for entry in ani_img}

        # Convert preprocessed CSV to a dictionary for quick access
        print("Converting preprocessed CSV to dictionary...")
        csv_dic = {row['name_english']: row for _, row in preprocessed_csv.iterrows()}

        # Convert Anime_Data.csv to a dictionary for quick access
        print("Converting Anime_Data.csv to dictionary...")
        new_csv_dic = new_csv.set_index('title_english')['genres'].to_dict()

        # Merge data
        print("Merging data...")
        enriched_data = []
        for anime in ani_data_full:
            # Use name_english or fallback to name
            key = anime.get("name_english") or anime.get("name")
            if not key:
                continue  # Skip entries with no name
            
            # Add img_url
            anime['img_url'] = img_dic.get(key, "No image available")

            # Enrich genres from preprocessed CSV
            if key in csv_dic:
                csv_entry = csv_dic[key]
                genres_str = csv_entry.get('genres')
                if pd.notna(genres_str):
                    genres = ast.literal_eval(genres_str)  # Convert string to list
                    anime['genres'] = [genre.lower() for genre in genres]
                else:
                    anime['genres'] = anime.get('genres', ["unknown"])

            # Add genres from Anime_Data.csv
            if key in new_csv_dic:
                new_genres = new_csv_dic[key]
                if pd.notna(new_genres):
                    new_genres_list = [g.strip().lower() for g in new_genres.split(',')]
                    current_genres = anime.get('genres', [])
                    anime['genres'] = list(set(current_genres + new_genres_list))

            enriched_data.append(anime)

        return enriched_data

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print("An error occurred during data preprocessing.")
        print(e)


def propagate_genres(data):
    # Create a dictionary mapping names to genres for fast lookup
    name_to_genres = {
        (anime.get("name_english") or anime.get("name") or "").lower(): anime.get("genres", [])
        for anime in data if anime.get("genres")
    }

    # Iterate over entries with missing genres
    for anime in data:
        if not anime.get("genres"):  # Missing genres
            anime_name = (anime.get("name_english") or anime.get("name") or "").lower()
            related_genres = set()

            # Check for similar names
            for key, genres in name_to_genres.items():
                if anime_name.startswith(key) or key.startswith(anime_name):
                    related_genres.update(genres)

            if related_genres:
                anime["genres"] = list(related_genres)

    return data



if __name__ == "__main__":
    print("Executing preprocess_data.py...")
    
    # Merge and enrich data
    enriched_data = merge_data()

    # Propagate genres to entries with missing genres
    print("Propagating missing genres...")
    final_data = propagate_genres(enriched_data)

    # Save the final dataset
    print("Saving final enriched data...")
    with open('data/final_anime_data.json', 'w', encoding='utf-8') as final_file:
        json.dump(final_data, final_file, indent=4, ensure_ascii=False)

    print("Data preprocessing complete. Final file saved as 'final_anime_data.json'.")
