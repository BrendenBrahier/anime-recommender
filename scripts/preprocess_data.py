import json

def merge_data():
    try:
        # load the json files 
        print("Loading data files...")
        with open('data/ani_data_full.json', 'r', encoding='utf-8') as details_file:
            ani_data_full = json.load(details_file)

        print("Loading image files...")
        with open('data/ani_img.json', 'r', encoding='utf-8') as img_file:
            ani_img = json.load(img_file)

        # convert ani_img.json to a dictionary for quick access
        print("Converting image data to dictionary...")
        img_dic = {entry["name_english"]: entry["img"] for entry in ani_img}

        # add img urls to ani_data_full.json
        print("Merging data...")
        for anime in ani_data_full:
            # check if the name_english is null, and use name instead
            key = anime["name_english"] if anime ["name_english"] else anime["name"]
            # add the img url to the anime data
            anime['img_url'] = img_dic.get(key, "No image available")

        # save the merged data to a new file
        print("Saving merged data...")
        with open('data/merged_anime_data.json', 'w', encoding='utf-8') as merged_file:
            json.dump(ani_data_full, merged_file, indent=4)

        print("Data preprocessing complete. Merged file saved as 'merged_anime_data.json'.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print("An error occurred during data preprocessing.")
        print(e)

if __name__ == "__main__":
    print("Executing preprocess_data.py...")
    merge_data()
    print("Finished executing preprocess_data.py.")