import pandas as pd
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the CSV file
csv_file_path = os.path.join(current_dir, "openrice_data.csv")

# Load the CSV file
df = pd.read_csv(csv_file_path)

# Display basic information about the dataset
print("Dataset Info:")
print(df.info())
print("\nFirst 5 rows:")
print(df.head())

# Basic analysis
# 1. Average rating by cuisine
avg_rating_by_cuisine = df.groupby('cuisine')['rating'].mean().sort_values(ascending=False)
print("\nAverage Rating by Cuisine:")
print(avg_rating_by_cuisine)

# 2. Most reviewed restaurants
most_reviewed = df[['name', 'review_count']].sort_values(by='review_count', ascending=False).head(10)
print("\nTop 10 Most Reviewed Restaurants:")
print(most_reviewed)

# 3. Price range distribution
price_distribution = df['price'].value_counts()
print("\nPrice Range Distribution:")
print(price_distribution)