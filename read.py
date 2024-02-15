import pandas as pd
from collections import Counter

#First of all, we reduce the database only to those business that are restaurants
df = pd.read_json("yelp_academic_dataset_business.json", lines=True)
restaurants_df = df[df['categories'].str.contains('Restaurants', na=False)]

#Then we can add some filters
#First we select a district we are interested in, after that we select a specific category.
restaurants_df = restaurants_df[restaurants_df['city'] == 'Philadelphia']
restaurants_df = restaurants_df[restaurants_df['categories'].str.contains('Italian', na=False)]

#Save a list of the restaurants that have come out of the filtering.
#THIS IS THE BACKBONE OF THE SCAPRING! WE LOOK FOR THE RESTAURANTS IDS WHAT ARE CONTAINED IN THIS LIST
restaurants_df.to_csv('list_filtered_restaurant.csv')

#Check how many restaurants included in the dataset
print(restaurants_df.count())



'''
AFTER this line it's just old code, not directly used for the analysis.
'''

#unique_to_df1 = restaurants_df[~restaurants_df['business_id'].isin(df_scrap['business_id'])]
#print(unique_to_df1.count())



'''
if __name__ == "__main__":
    #City with max amount of businesses
    city_counts = df.groupby('city')['city'].count()
    top_10_cities = city_counts.sort_values(ascending=False).head(15)

    for city, count in top_10_cities.items():
        print(city, count)


    # Filter the DataFrame to include only businesses in the city of Philadelphia
    philadelphia_restaurants_df = restaurants_df[restaurants_df['city'] == 'Philadelphia']

    # Generate a list of categories for businesses in Philadelphia
    all_categories = [category.strip() for sublist in philadelphia_restaurants_df['categories'].dropna().str.split(',') for category in sublist]

    # Count the categories and print the most common 30
    counter = Counter(all_categories)
    print(counter.most_common(30))
'''
