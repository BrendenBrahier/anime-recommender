# check the number of entries
import json

def number_of_entries():
    with open("data/merged_anime_data.json", "r", encoding="utf-8") as merged_file:
        merged_data = json.load(merged_file)

    # calculate the number of rows and total data points
    num_rows = len(merged_data) # number of entries (rows)
    num_data_points = sum(len(anime) for anime in merged_data) # total data points

    print(f"Number of entries: {num_rows}")
    print(f"Total data points: {num_data_points}")


if __name__ == "__main__":
    print("Executing num_of_entries.py...")
    number_of_entries()
    print("Finished executing num_of_entries.py.")