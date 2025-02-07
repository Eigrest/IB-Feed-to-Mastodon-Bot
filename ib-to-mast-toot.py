import os

import chromedriver_autoinstaller
from mastodon import Mastodon
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

mast_tag = "Eigrest_IB_bot"

# create webdriver object
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

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://infinitebacklog.net/users/eigrest")
WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "post")))
feed = driver.find_elements("xpath", '//*[contains(@class,"COLLECTION_GAME_COMPLETION") or contains(@class,"COLLECTION_GAME_STATUS")]')
posts = []
for post in feed:
    posts.extend(post.find_elements("xpath", './*[contains(@class, "message-post")]'))
posts_texts = []
for post in posts:
    posts_texts.append(post.text)

driver.close()

# get latest toot from account and tag
mastodon = Mastodon(
    access_token = os.environ['KEY'],
    api_base_url = os.environ['INS']
    )
last_toot_text = mastodon.account_statuses(mastodon.me().get("id"),False,False,
                                True,True,mast_tag,
                                None,None,None,None)[0].content

#get to chosen post_text after latest toot posted
i=0
chosen_post = ""
uptodate = False
for post_text in posts_texts:
    if post_text.lower() in last_toot_text.lower():
        if i<=0:
            print("Toots up to date")
            uptodate = True
        else:
            chosen_post = posts_texts[i - 1]
        break
    else:
        i=i+1

if not uptodate and chosen_post:
    # toot post
    text_to_publish = chosen_post + " #" + mast_tag
    print("time to toot! " + text_to_publish)
    mastodon.status_post(text_to_publish,None,None,False,"unlisted")
else:
    print("no tooting today")
