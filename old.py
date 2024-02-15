from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from scrap import append_batch_to_csv
from read import restaurants_df
import time
import random

# Setup and initialization
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)  # wait for up to 10 seconds

#empty dataset
data = []
BATCH_SIZE = 1000


def scrape_page(business_id):
    global data
    parent_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.not-recommended-reviews')))
    h3_element = parent_div.find_element(By.CSS_SELECTOR, 'h3')
    shown_reviews = parent_div.find_elements(By.CSS_SELECTOR, 'ul.ylist li div.review')
    h3_text = h3_element.text #will make use of this maybe later
    print(h3_text)

    for index, review_div in enumerate(shown_reviews, start=1):
        print(f'Review number: {index}')

        # Base elements Review-Wrapper (Score, Review, Date)
        review_wrapper = review_div.find_element(By.CSS_SELECTOR, 'div.review-wrapper')
        review_content = review_wrapper.find_element(By.CSS_SELECTOR, 'div.review-content')

        # Extract rating
        rating = review_content.find_element(By.CSS_SELECTOR, 'div.biz-rating div.biz-rating__stars div.rating-large').get_attribute('title')
        # Extract date
        date = review_content.find_element(By.CSS_SELECTOR, 'span.rating-qualifier').text
        # Extract review details
        review = review_content.find_element(By.CSS_SELECTOR, 'p') 
        language = review.get_attribute('lang')
        text = review.text

        # Base elements Review-Sidebar (User info)
        review_content = review_div.find_element(By.CSS_SELECTOR, 'div.review-sidebar')
        review_sidebar_content = review_content.find_element(By.CSS_SELECTOR, 'div.review-sidebar-content')
        review_sidebar_img = review_sidebar_content.find_element(By.CSS_SELECTOR, 'div.ypassport div.media-avatar')
        review_sidebar__media_story = review_sidebar_content.find_element(By.CSS_SELECTOR, 'div.ypassport div.media-story')
        

        #TO-DO #Extract user's info (picture)

        review_sidebar_img = review_sidebar_content.find_element(By.CSS_SELECTOR, 'div.ypassport div.media-avatar div.photo-box img').get_attribute('srcset') 
        #has_srcset = review_sidebar_img.get_attribute('srcset') is not None #if there is this attribute, there is an img, otherwise nope
        

        #Extract user's info (data - 2 lists)
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


        try:
            photo_count_text = user_passport_stats_ul.find_element(By.CSS_SELECTOR, 'li.photo-count').text
        except:
            pass

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
        data.append(row)

        if len(data) >= BATCH_SIZE:
            append_batch_to_csv(data)
            print('100 analised!')
            data = []  # Clear the batch

#just info for the console
total = restaurants_df["business_id"].count()
current = 1
start_time = time.time()



# Start by clicking the "not recommended reviews" link
for business_id in restaurants_df["business_id"]:

    time.sleep(random.uniform(5, 15))
    
    print(f'analasying busines id: {business_id}, this is the {current} of {total}')

    driver.get(f"https://www.yelp.at/biz/{business_id}")
    driver.maximize_window()

    

    try: #to find if there are any "not-reccomended-reviews"
        element = driver.find_element(By.XPATH, '//a[contains(@href, "/not_recommended_reviews")]') #here written with _
        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()
    except NoSuchElementException as e: #no reccomended reviews, so go to next restaurant
        print(f'this happened: {e}')
        continue

    while True:
        try:
            scrape_page(business_id)  # Scraping logic for the current page

            # Try to find the "next" button and click it
            ##PROBLEM: NEXT BUTTON CAN ALSO APPEAR IN THE OTHER SECTION
            next_button = driver.find_element(By.XPATH, "//div[contains(@class, 'not-recommended-reviews')]//a[contains(@class, 'next')]")
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(random.uniform(2, 8))
            next_button.click()
        except NoSuchElementException:  # If "next" button isn't found
            print("End: No more pages.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    
    current += 1
    elapsed_time = time.time() - start_time  
    print(f"Running since start: {elapsed_time:.2f} seconds")

if data:  # Check if there's any leftover data
    df_final = pd.DataFrame(data)
    df_final.to_csv('scraped_data.csv', mode='a', header=False, index=False)