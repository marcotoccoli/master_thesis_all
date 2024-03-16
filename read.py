import pandas as pd
from collections import Counter

#First of all, we reduce the database only to those business that are restaurants
#df = pd.read_json("yelp_academic_dataset_business.json", lines=True)
#restaurants_df = df[df['categories'].str.contains('Restaurants', na=False)]

#Then we can add some filters
#First we select a district we are interested in, after that we select a specific category.
#restaurants_df = restaurants_df[restaurants_df['city'] == 'Philadelphia']
#restaurants_df = restaurants_df[restaurants_df['categories'].str.contains('Italian', na=False)]

#Save a list of the restaurants that have come out of the filtering.
#THIS IS THE BACKBONE OF THE SCAPRING! WE LOOK FOR THE RESTAURANTS IDS WHAT ARE CONTAINED IN THIS LIST
#restaurants_df.to_csv('list_filtered_restaurant.csv')

