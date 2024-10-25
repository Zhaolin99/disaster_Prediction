from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

"""
Before run the program: Due to protection from X(Twitter), it might block its search function temporarily.
To avoid this condition, please do not set scroll_attempts over 10 times and do not scrape more than two URLs once.
If the search function is blocked, you can try to logout your X account, then exit and reopen your browser,
and it should reset the cookies. You will need to reset your Cookies in this program to scrape tweets normally.
"""


# List of cookies
# NOTE: It needs to be reset based on browser and X account
"""
It can be found in Chrome from developer tool bar. Application -> Storage -> Cookies.
Please copy the cookies under X.com with the format below. 
Note different browsers could have different cookies set-ups.
"""
COOKIES = [
    {"name": "auth_token", "value": " ", "domain": ".x.com"},
    {"name": "ct0", "value": " ", "domain": ".x.com"},
    {"name": "dnt", "value": "1", "domain": ".x.com"},
    {"name": "g_state", "value": '{"i_l":0}', "domain": ".x.com"},
    {"name": "gt", "value": " ", "domain": ".x.com"},
    {"name": "guest_id", "value": " ", "domain": ".x.com"},
    {"name": "guest_id_ads", "value": " ", "domain": ".x.com"},
    {"name": "guest_id_marketing", "value": " ", "domain": ".x.com"},
    {"name": "kdt", "value": " ", "domain": ".x.com"},
    {"name": "lang", "value": "en", "domain": ".x.com"},
    {"name": "night_mode", "value": "2", "domain": ".x.com"},
    {"name": "personalization_id", "value": '' ".x.com"},
    {"name": "twid", "value": " ", "domain": ".x.com"}
]

# Function to initialize Selenium WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Use WebDriverManager to manage ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# Function to scrape tweets
def scrape_tweets(search_url):
    driver = init_driver()
    # Add cookies on the Homepage
    driver.get("https://x.com")

    # Add cookies to the browser
    for cookie in COOKIES:
        driver.add_cookie(cookie)
    # Navigate to the search URL
    driver.get(search_url)
    tweet_texts = []

    try:
        # Wait for Loading
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetText']"))
        )

        # Initialize variables for scrolling
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 10  # Number of scrolls before stopping (Keep below 10)

        while scroll_attempts > 0:
            # Extract tweet text content only
            tweet_elements = driver.find_elements(By.XPATH, "//div[@data-testid='tweetText']")
            for tweet in tweet_elements:
                tweet_text = tweet.text
                if tweet_text not in tweet_texts:  # Avoid duplicates
                    tweet_texts.append(tweet_text)

            # Scroll down to load more tweets
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts -= 1
            else:
                last_height = new_height

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

    return tweet_texts


import csv
urls = [
    'https://x.com/search?q=wildfire&src=typed_query&f=top',
    'https://x.com/search?q=storm&src=typed_query&f=top',
    'https://x.com/search?q=tornado&src=typed_query&f=top',
    'https://x.com/search?q=Landslide&src=typed_query'
]

# Collect Tweets from Each search URLs (includes wildfire, storm, tornado, landslide)
all_tweets = []
for url in urls:
    tweets = scrape_tweets(url)
    all_tweets.extend(tweets)

# Export all tweets to a CSV file
with open("tweets.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["tweet"])
    for tweet in all_tweets:
        writer.writerow([tweet])

print("Tweets have been exported to tweets.csv.")
