from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from read import restaurants_df
import time
import random
import csv
import os

# Setup and initialization
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)  # wait for up to 10 seconds

# Empty dataset --> there is a BATCH logic that at the end I haven't used. 
data_not_recommended, data_removed = [], []
#BATCH_SIZE = 1000

def append_batch_to_csv(rows, filename):
    # Check if the file exists 
    file_exists = os.path.isfile(f'{filename}.csv')

    with open(f'{filename}.csv', 'a', newline='') as csvfile:
        fieldnames = ['business_id', 'user_name', 'user_location', 'has_image', 'friends_count', 'reviews_count', 'photos_count', 'rating', 'review_date', 'language', 'review_text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # If the file is not found, write the headers
        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)


def scrape_page(business_id, review_type):
    global data_not_recommended, data_removed
    #There are 2 main div that act as container --> div.not-recommended-reviews / div.removed-reviews
    # in the first line we identify the div we are currently interested in, after that we extract the ul element they contain
    parent_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'div.{review_type}')))
    shown_reviews = parent_div.find_elements(By.CSS_SELECTOR, 'ul.ylist li div.review')

    #Use to manually check if all reviews are there, because it prints "X reviews for business Y are shown"
    h3_element = parent_div.find_element(By.CSS_SELECTOR, 'h3')
    h3_text = h3_element.text 
    print(h3_text)

    #At this point we loop for each li in the ul
    for index, review_div in enumerate(shown_reviews, start=1):
        print(f'Review number: {index}')

        # Review-Content and Review-Side-Bar!!!
        # A 'li - review' has two blocks, the content (right side, shows details of the review) and the Side-Bar (left side, shows details of the reviewer)

        #Logic for the Content
        review_wrapper = review_div.find_element(By.CSS_SELECTOR, 'div.review-wrapper')
        review_content = review_wrapper.find_element(By.CSS_SELECTOR, 'div.review-content')

        # Extract rating
        rating = review_content.find_element(By.CSS_SELECTOR, 'div.biz-rating div.biz-rating__stars div.rating-large').get_attribute('title')
        # Extract date
        date = review_content.find_element(By.CSS_SELECTOR, 'span.rating-qualifier').text
        # Extract review details (contant and the language)
        review = review_content.find_element(By.CSS_SELECTOR, 'p') 
        language = review.get_attribute('lang')
        text = review.text

        #Logic for the Side-Bar
        review_content = review_div.find_element(By.CSS_SELECTOR, 'div.review-sidebar')
        review_sidebar_content = review_content.find_element(By.CSS_SELECTOR, 'div.review-sidebar-content')
        review_sidebar_img = review_sidebar_content.find_element(By.CSS_SELECTOR, 'div.ypassport div.media-avatar')
        review_sidebar__media_story = review_sidebar_content.find_element(By.CSS_SELECTOR, 'div.ypassport div.media-story')
        
        #If there is an avatar, the img tag as a source attribute.
        review_sidebar_img = review_sidebar_content.find_element(By.CSS_SELECTOR, 'div.ypassport div.media-avatar div.photo-box img').get_attribute('srcset') 
        #has_srcset = review_sidebar_img.get_attribute('srcset') is not None #if there is this attribute, there is an img, otherwise nope
        
        #Extract user's info (user info are spread in two ul, we go through each one)

        #First list -> name, place
        user_passport_info_ul = review_sidebar__media_story.find_element(By.CSS_SELECTOR, 'ul.user-passport-info')
        user_name_li = user_passport_info_ul.find_element(By.CSS_SELECTOR, 'li.user-name')
        user_location_li = user_passport_info_ul.find_element(By.CSS_SELECTOR, 'li.user-location')

        user_name_text = user_name_li.text
        user_location_text = user_location_li.text

        #Second list -> Freunde, Beiträge, Fotos
        user_passport_stats_ul = review_sidebar__media_story.find_element(By.CSS_SELECTOR, 'ul.user-passport-stats')
        friend_count_text = user_passport_stats_ul.find_element(By.CSS_SELECTOR, 'li.friend-count b').text
        review_count_text = user_passport_stats_ul.find_element(By.CSS_SELECTOR, 'li.review-count b').text
        photo_count_text = 0

        #Logic to avoit problem with wrong photo count
        try:
            photo_count_text = user_passport_stats_ul.find_element(By.CSS_SELECTOR, 'li.photo-count').text
        except:
            pass
        
        #Summarize the info in a row  dict -like
        row = {
            'business_id': business_id,
            'user_name': user_name_text,
            'user_location': user_location_text,
            'has_image': True if review_sidebar_img else False,
            'friends_count': friend_count_text,
            'reviews_count': review_count_text,
            'photos_count': photo_count_text,
            'rating': rating,
            'review_date': date,
            'language': language,
            'review_text': text
        }

        #Append the row to the right "database - list" (check argument of this function)
        if review_type == 'not-recommended-reviews':
            data_not_recommended.append(row)
            #data = data_not_recommended
        else:
            data_removed.append(row)
            #data = data_removed

        
        '''
        if len(data) >= BATCH_SIZE:
            append_batch_to_csv(data, review_type)
            print('100 analysed!')
            
            # Clear the batch data
            if review_type == 'not-recommended-reviews':
                data_not_recommended = []
            else:
                data_removed = []
        '''


# Just info for the console
total = restaurants_df["business_id"].count()
current = 1
start_time = time.time()

# Start by clicking the "not recommended reviews" link
# We loop from every business id from the dataset they provided after having filtered.
for business_id in restaurants_df["business_id"]:   
    #time.sleep(random.uniform(5, 15)) --> needed?
    print(f'analysing business id: {business_id}, this is the {current} of {total}')
    driver.get(f"https://www.yelp.at/biz/{business_id}")
    driver.maximize_window()

    # Try to access the not-recommended-reviews page (both review type are here, even the 'removed')
    try:  
        element = driver.find_element(By.XPATH, '//a[contains(@href, "/not_recommended_reviews")]')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()
    #If this button is not present, it means there are no reviews we are interested in 
    except NoSuchElementException as e:  
        print(f'this happened: {e}')
        continue
    
    # At this point we are in the page where all reviews are listed

    # We loop for the 2 type of reviews we want, the html is similar, just some attributes change. See dict below.
    review_types_data = {
        'not-recommended-reviews': 'not_recommended_start',
        'removed-reviews': 'removed_start'
    }

    for review_type, href_contains in review_types_data.items():
        while True:
            try:
                scrape_page(business_id, review_type=review_type)  # Scraping logic for the current page (the one direct after clicking "not-recommended")
                # Try to find the "next" button and click it (a page can contain max 10 reviews)
                next_button = driver.find_element(By.XPATH, f"//div[contains(@class, '{review_type}')]//a[contains(@class, 'next') and contains(@href, '{href_contains}')]")
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                time.sleep(random.uniform(5, 10)) # this line slows down the code, is it needed? 
                next_button.click()
            except NoSuchElementException:  # If "next" button isn't found
                print(f"End of {review_type}. No more pages.")
                break
            #This second Expetion block is likely triggered if there are no removed-reviews and therefor the path above is false
            except Exception as e:
                print(f"An error occurred")
                break
        
        #Not really optimal because we open the files every time we are done with a restaurant. Reviews stored in memory for a while.
        if review_type == 'not-recommended-reviews' and data_not_recommended:
            append_batch_to_csv(data_not_recommended, review_type)  
            data_not_recommended = []  # Reset the list - this was filled during the scrape_page function

        elif review_type == 'removed-reviews' and data_removed:
                append_batch_to_csv(data_removed, review_type)
                data_removed = []  # Reset the list

    #info for the console
    current += 1
    elapsed_time = time.time() - start_time  
    print(f"Running since start: {elapsed_time:.2f} seconds")

#There two ifs are not really needed, they just catch if for some reasons some data are still in the []
if data_not_recommended:  # Check if there's any leftover data
    df_final = pd.DataFrame(data_not_recommended)
    df_final.to_csv('not-recommended-reviews.csv', mode='a', header=False, index=False)

if data_removed:  # Check if there's any leftover data
    df_final = pd.DataFrame(data_removed)
    df_final.to_csv('removed-reviews.csv', mode='a', header=False, index=False)

print('we are done :)')