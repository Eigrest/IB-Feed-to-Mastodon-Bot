import os
import re
import chromedriver_autoinstaller

from dotenv import load_dotenv
from mastodon import Mastodon
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

MAST_TAG = "Eigrest_IB_bot"

def load_page(uri):
    driver.get(uri)
    # Waits page to load.
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "post")))

def filter_game_updates():
    feed = driver.find_elements("xpath", '//*[contains(@class,"COLLECTION_GAME_COMPLETION") or contains(@class,"COLLECTION_GAME_STATUS")]')
    return [
        element
        for post in feed
        for element in post.find_elements("xpath", './*[contains(@class, "message-post")]')
    ]
            
def format_game_updates_text():
    return [
        # removes x days ago text and adds rating
        re.sub(r"- \d+.*", "", element.text) + add_game_ratings(element)
        for element in game_updates_elements
    ]

def add_game_ratings(element):
    star_map = {"100%": "🌕", "50%": "🌗", "0%": "🌑"}

    return "".join(
        star_map.get(
            star.find_element(By.TAG_NAME,"stop").get_attribute("offset"), ""
        )
        for star_rating in element.find_elements(By.CLASS_NAME, "star-rating-star")
        for star in star_rating.find_elements(By.TAG_NAME, "svg")
    )

def get_latest_bot_toot():
    last_toot = mastodon.account_statuses(mastodon.me().get("id"),False,False,
                                    True,True,MAST_TAG,
                                    None,None,None,None)[0].content
    #normalize toot for later matching
    last_toot = re.sub(r'\s+', ' ', last_toot.replace('<br />', ' ').replace('<p>', '').replace('</p>', '').strip()).lower()
    
    print("last toot:")
    print(last_toot)
    return last_toot

def is_game_update_in_toot(game_update):
    normalized_game_update = " ".join(game_update.split()).lower()
    if normalized_game_update in last_toot:
        return True
    else:
        return False   

def post_game_update_toot(game_update):
    text_to_publish = game_update + " #" + MAST_TAG
    print("posting this game update:")
    print(text_to_publish)
    mastodon.status_post(text_to_publish,None,None,False,"unlisted")

def get_next_game_update():
    print("Possible toots:")
    for i, game_update in enumerate(game_updates_list):
        print(game_update)
        if is_game_update_in_toot(game_update):
            return game_updates_list[i-1]
 

########################################

# Create webdriver that Selenium uses to access the web page.
display = Display(visible=0, size=(800, 800))
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
# and if it doesn't exist, download it automatically,
# then add chromedriver to path

chrome_options = webdriver.ChromeOptions()
options = [
    "--window-size=1200,1200",
    "--ignore-certificate-errors"
]

for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome()
load_page("https://infinitebacklog.net/users/eigrest")

game_updates_elements = filter_game_updates()
game_updates_list = format_game_updates_text()

driver.close()

load_dotenv()

mastodon = Mastodon(
    access_token = os.environ['KEY'],
    api_base_url = os.environ['INS']
    )

last_toot = get_latest_bot_toot()

# if latest update was already posted no toots today. 
if is_game_update_in_toot(game_updates_list[0]):
    print("Toots up to date. No tooting today.")

# if no update partially matches with the last toot post oldest update
elif not any(is_game_update_in_toot(update) for update in game_updates_list):
    post_game_update_toot(game_updates_list[-1])

# get following update after last toot
else:
    post_game_update_toot(get_next_game_update())