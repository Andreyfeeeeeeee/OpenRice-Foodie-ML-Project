import pandas as pd
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the classified CSV file
csv_file_path = os.path.join(current_dir, "classified_foodie_data.csv")

# Load the CSV file
df = pd.read_csv(csv_file_path)

# Select features for clustering (e.g., rating, review_count, price)
# Convert price to numerical values (e.g., extract the lower bound of the range)
df['price_lower'] = df['price'].str.extract(r'(\d+)').astype(float)

# Features for clustering
features = ['rating', 'review_count', 'price_lower']
X = df[features].fillna(0)  # Fill missing values with 0

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply K-Means clustering
kmeans = KMeans(n_clusters=3, random_state=42)
df['cluster'] = kmeans.fit_predict(X_scaled)

# Save the clustered data
output_csv_path = os.path.join(current_dir, "clustered_foodie_data.csv")
df.to_csv(output_csv_path, index=False, encoding='utf8')
print(f"Clustered data saved to {output_csv_path}")

# Display the cluster distribution
cluster_distribution = df['cluster'].value_counts()
print("\nCluster Distribution:")
print(cluster_distribution)

# Analyze clusters
cluster_analysis = df.groupby('cluster')[features].mean()
print("\nCluster Analysis (Mean Values):")
print(cluster_analysis)