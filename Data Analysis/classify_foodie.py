import pandas as pd
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the CSV file
csv_file_path = os.path.join(current_dir, "openrice_data.csv")

# Load the CSV file
df = pd.read_csv(csv_file_path)

# Define a function to classify foodie type based on restaurant data
def classify_foodie(row):
    if row['rating'] > 4.0 and row['review_count'] > 100:
        return "YouTuber"
    elif row['price'] in ['$201-400', '$401-800'] and pd.notna(row['special_dish']) and row['special_dish'] != "":
        return "IG Creator"
    else:
        return "Regular Foodie"

# Apply the classification
df['foodie_type'] = df.apply(classify_foodie, axis=1)

# Save the classified data to a new CSV
output_csv_path = os.path.join(current_dir, "classified_foodie_data.csv")
df.to_csv(output_csv_path, index=False, encoding='utf8')
print(f"Classified data saved to {output_csv_path}")

# Display the distribution of foodie types
foodie_distribution = df['foodie_type'].value_counts()
print("\nFoodie Type Distribution:")
print(foodie_distribution)