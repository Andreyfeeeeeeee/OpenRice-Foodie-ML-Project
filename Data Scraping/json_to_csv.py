import json
import pandas as pd
import os

def json_to_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='utf8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False, encoding='utf8')
    print(f"Data has been converted from {json_file} to {csv_file}")

current_dir = os.path.dirname(os.path.abspath(__file__))

json_file_path = os.path.join(current_dir, "openrice_data.json")
csv_file_path = os.path.join(current_dir, "openrice_data.csv")

if not os.path.exists(json_file_path):
    print(f"Error")
else:
    json_to_csv(json_file_path, csv_file_path)