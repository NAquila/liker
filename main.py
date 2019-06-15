from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import json
from time import sleep
import pandas as pd
from bot import InstagramBot
from insta_pages import LogInPage, ProfilePage
import logging
from logging import StreamHandler
import sys


logger = logging.getLogger('insta_pages')
h = StreamHandler(sys.stdout)
logger.addHandler(h)
logger.setLevel(logging.DEBUG)
bot = InstagramBot()
bot.log_in()

followers = bot.read_followers('juliakbrou')

with open('credentials.json', 'r') as f:
    cred = json.load(f)
# opts = Options()
# opts.set_headless()
browser = webdriver.Firefox()
browser.get('https://www.instagram.com')

log_in = browser.find_element_by_link_text('Log in')
log_in.click()
username = browser.find_element_by_name('username')
username.send_keys(cred['username'])
pwd = browser.find_element_by_name('password')
pwd.send_keys(cred['password'])

buttons = browser.find_elements_by_tag_name('button')
for button in buttons:
    if button.text ==  'Log In':
        login = button
login.click()

buttons = browser.find_elements_by_tag_name('button')
for button in buttons:
    if button.text ==  'Not Now':
        notnow = button
notnow.click()

inputs = browser.find_elements_by_tag_name('input')
for inp in inputs:
    # Safety check to avoid traps
    if inp.is_displayed():
        if inp.get_property('placeholder') == 'Search':
            search_form = inp

search_form.send_keys('juliakbrou')
search_form.send_keys(Keys.ARROW_DOWN)
search_form.send_keys(Keys.RETURN)

# Get followers
anchors = browser.find_elements_by_tag_name('a')
for anchor in anchors:
    if anchor.is_displayed():
        if 'followers' in anchor.text:
            follower_anchor = anchor
import re

follower_anchor.click()

# Locate div that holds followers
buttons = browser.find_elements_by_tag_name('button')
for b in buttons:
    if b.text == 'Follow':
        div = b.find_element_by_xpath('./../../../../../..')
        break

PDOWN_WAIT = 0.1
for i in range(3):
    ActionChains(browser).move_to_element(div).click().send_keys(Keys.PAGE_DOWN).perform()
    sleep(PDOWN_WAIT)




account_texts = ('Follow', 'Following', 'Requested')
followers_tuples = []
for b in buttons:
    if b.text in account_texts:
        list_item = b.find_element_by_xpath('./../../..')
        account_name = list_item.text.split('\n')[0]
        status = b.text
        followers_tuples.append((account_name, status))
followers_df = pd.DataFrame(followers_tuples,
                            columns=('name', 'status'))


print(results)
browser.close()
