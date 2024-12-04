import pandas as pd
import json

def prepare_frontend_data(input_file, output_file):
    # load the dataset
    data = pd.read_json(input_file)

    # fill missing values 
    data['genres'] = data['genres'].apply(lambda x: x if isinstance(x, list) else ["unknown"])
    data['img_url'] = data['img_url'].fillna("unknown")
    data['type_of'] = data['type_of'].fillna("unknown").str.lower().replace(" ", "")
    data['start_date'] = pd.to_datetime(data['start_date'], errors='coerce')
    data['score'] = data['score'].fillna(0)

    # Extract year from start_date
    data['year'] = data['start_date'].dt.year.fillna(0).astype(int)

    #keep only relevant fields
    frontend_data = data[['name_english', 'score', 'ranked', 'popularity', 'members', 'genres', 'type_of', 'studios', 'img_url', 'year']]

     # Convert DataFrame to a list of dictionaries
    data_list = frontend_data.to_dict(orient='records')

    # Save the data without escaping slashesS
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=4, ensure_ascii=False)

    print(f"Frontend data saved to {output_file}")

if __name__ == "__main__":
    prepare_frontend_data('data/cleaned_anime_data.json', 'data/frontend_data.json')

