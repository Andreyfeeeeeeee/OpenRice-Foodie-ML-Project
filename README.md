# OpenRice Foodie ML Project

## Purpose
This project scrapes restaurant data from OpenRice, analyzes foodie preferences, classifies foodie types (e.g., YouTuber, IG Creator), and applies machine learning to cluster restaurants.

## Methods
- **Data Scraping**: Used Selenium and BeautifulSoup to scrape OpenRice.
- **Data Processing**: Converted JSON to CSV using pandas.
- **Analysis**: Analyzed restaurant features (rating, review count, price).
- **Classification**: Classified foodies based on rules.
- **Machine Learning**: Applied K-Means clustering to group restaurants.

## Results
- Classified foodies into YouTuber, IG Creator, and Regular Foodie.
- Clustered restaurants into 3 groups based on rating, review count, and price.

## How to Run
1. Install dependencies: `pip install selenium webdriver_manager beautifulsoup4 pandas scikit-learn`
2. Run `scraping.py` to scrape data.
3. Run `json_to_csv.py` to convert JSON to CSV.
4. Run `data_analysis.py` for basic analysis.
5. Run `classify_foodie.py` to classify foodies.
6. Run `kmeans_clustering.py` for clustering.
