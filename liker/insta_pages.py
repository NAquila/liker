from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import logging
import re
import random


logger = logging.getLogger(__name__)


class WrongPageError(Exception):
    pass


class _InstaPage(object):
    """Base class for all instagram pages."""
    def __init__(self, driver):
        self.driver = driver

    def wait(self):
        wait_base = 0.5
        noise = random.expovariate(1/wait_base)
        actual_wait = wait_base + noise
        logger.debug('Waiting {:.1f} ms'.format(1000*actual_wait))
        time.sleep(actual_wait)

    def short_wait(self):
        wait_base = 0.05
        noise = random.expovariate(1/wait_base)
        actual_wait = wait_base + noise
        logger.debug('Waiting {:.1f}ms'
                     .format(1000*actual_wait))
        time.sleep(actual_wait)

    def close(self):
        """Closes the driver linked to this page."""
        self.driver.close()


class LogInPage(_InstaPage):
    """The first page reached when going to instagram."""
    def verify_url(self):
        """Verifies that the current url is 'https://www.instagram.com'."""
        curr_url = self.driver.current_url
        if curr_url != 'https://www.instagram.com/':
            msg = '{} is not the login url for instagram'.format(curr_url)
            raise WrongPageError(msg)

    def log_in(self, cred):
        self.verify_url()
        log_in = self.driver.find_element_by_link_text('Log in')
        log_in.click()
        logger.info('Acessing log-in page...')
        self.wait()
        logger.info('Sending credentials...')
        username = self.driver.find_element_by_name('username')
        username.send_keys(cred['username'])
        self.short_wait()
        pwd = self.driver.find_element_by_name('password')
        pwd.send_keys(cred['password'])
        logger.info('Logging in...')
        self.short_wait()
        buttons = self.driver.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Log In':
                login = button
        login.click()
        for i in range(5):
            self.wait()
        # Get rid of annoying pop-up
        buttons = self.driver.find_elements_by_tag_name('button')
        for button in buttons:
            if button.text == 'Not Now':
                logger.debug('Removing pop-up')
                notnow = button
                notnow.click()
        logger.info('Logged in sucessfully!')


class MainPage(_InstaPage):

    def verify_url(self):
        """Verifies that the current url is 'https://www.instagram.com'."""
        curr_url = self.driver.current_url
        if curr_url != 'https://www.instagram.com/':
            msg = '{} is not the login url for instagram'.format(curr_url)
            raise WrongPageError(msg)

    def _find_search_form(self):
        inputs = self.driver.find_elements_by_tag_name('input')
        for inp in inputs:
            # Safety check to avoid traps
            if inp.is_displayed():
                if inp.get_property('placeholder') == 'Search':
                    search_form = inp

        if search_form is None:
            msg = 'Search form could not be found!'
            raise WrongPageError(msg)
        else:
            return search_form

    def goto_first_result(self, query):
        search_form = self._find_search_form()
        search_form.send_keys(query)
        search_form.send_keys(Keys.ARROW_DOWN)
        search_form.send_keys(Keys.RETURN)


class ProfilePage(_InstaPage):
    """Base-class for a generic profile page"""

    def __init__(self, driver, profile):
        super().__init__(driver)
        self.profile = profile

    def goto_url(self):
        """Moves to this profile page"""
        self.driver.get('https://www.instagram.com/{}/'.format(self.profile))

    def verify_url(self):
        """Verifies that the current url is
        'https://www.instagram.com/name_of_profile'."""
        if not self.correct_url():
            msg = ('{} is not the login url for instagram'
                   .format(self.driver.curr_url))
            raise WrongPageError(msg)

    def on_url(self):
        """Returns if we are on the correct url or not."""
        curr_url = self.driver.current_url
        on_url = (curr_url ==
                  'https://www.instagram.com/{}/'.format(self.profile))
        return on_url

    def _get_follow_button(self):
        buttons = self.driver.find_elements_by_tag_name('button')
        for b in buttons:
            if b.is_displayed():
                if b.text in ('Following', 'Follow', 'Requested'):
                    follow_button = b
                    break
        return follow_button

    def is_private(self):
        """Check if an account is private."""
        # Currently just scans for an h2-heading with the word
        # 'Private' in it. This could easily fail if Instagram changes
        # their layout.
    def get_follow_status(self):
        follow_button = self._get_follow_button()
        return follow_button.text

    def follow(self):
        """Follow a user if not already following"""
        follow_button = self._get_follow_button()
        logger.info('Attempting to follow user {}'.format(self.profile))
        follow_button.click()
        self.short_wait()

    def unfollow(self):
        """Unfollow a user if user is being followed"""
        follow_button = self._get_follow_button()
        logger.info('Attempting to unfollow user {}'.format(self.profile))
        follow_button.click()
        self.short_wait()
        # After clicking the follow button a popup is presented to verify
        buttons = self.driver.find_elements_by_tag_name('button')
        for b in buttons:
            if b.is_displayed():
                if b.text == 'Unfollow':
                    popup_button = b
                    break
        popup_button.click()
        self.short_wait()

    def get_followers(self):
        """Gets the followers of a given profile"""
        num_followers = self.get_num_followers()
        self.short_wait()
        self._open_followers_window()
        for i in range(2):
            self.wait()
        self._load_followers(number=num_followers)
        self.wait()
        followers_df = self._read_displayed_followers()
        return followers_df

    def get_num_followers(self):
        logger.debug('Locating follower anchor...')
        anchors = self.driver.find_elements_by_tag_name('a')
        for anchor in anchors:
            if anchor.is_displayed():
                if 'followers' in anchor.text:
                    follower_anchor = anchor
        logger.debug('Parsing information to find number of followers')
        # regexp find all numbers with suffixes, e.g. 21.3k
        num_str = re.findall(r'\d+\,?\.?\d+[km]?', follower_anchor.text)[0]
        # remove commas
        num_str = num_str.replace(',', '')
        # Turn suffixes into a number
        if 'k' in num_str:
            num_str = num_str.replace('k', '')
            factor = 1000
        elif 'm' in num_str:
            factor = 10000000
            num_str = num_str.replace('m', '')
        else:
            factor = 1
        num_followers = float(num_str) * factor
        logger.debug('Profile {} has {} followers'
                     .format(self.profile, num_followers))
        return num_followers

    def _open_followers_window(self):
        anchors = self.driver.find_elements_by_tag_name('a')
        for anchor in anchors:
            if anchor.is_displayed():
                if 'followers' in anchor.text:
                    follower_anchor = anchor

        follower_anchor.click()

    def _load_followers(self, number):
        # Locate div that holds followers
        buttons = self.driver.find_elements_by_tag_name('button')
        for b in buttons:
            if b.text == 'Follow':
                div = b.find_element_by_xpath('./../../../../../..')
                break

        def page_down():
            logger.debug('Pushing pagedown in follower window')
            (ActionChains(self.driver)
             .move_to_element_with_offset(div, xoffset=1, yoffset=1)
             .click().send_keys(Keys.PAGE_DOWN).perform())

        # Read the followers before and after pressing pagedown once
        # to determine how many new followers one press yields

        # Press the pagedown key number of times. This will keep going
        # down the list of followers, loading more
        displayed_before = 0

        def get_num_list_items():
                logger.debug('Reading list_items')
                list_items = self.driver.find_elements_by_tag_name('li')
                return len(list_items)

        while True:
            logger.debug('Pressing page down and'
                         ' waiting for new followers')
            page_down()
            try:
                def check_new_displayed(driver):
                    num_new = get_num_list_items()
                    if num_new > displayed_before:
                        return num_new
                    else:
                        logger.debug('No new followers displayed')
                        return False
                displayed_before = (WebDriverWait(self.driver, 60)
                                    .until(check_new_displayed))
            except TimeoutException:
                logger.debug('Timed out waiting for new followers,'
                             ' exiting loop.')
                break

    def _read_displayed_followers(self):
        account_texts = ('Follow', 'Following', 'Requested')
        followers = []
        logger.debug('Reading followers')
        buttons = self.driver.find_elements_by_tag_name('button')
        for b in buttons:
            if b.text in account_texts:
                list_item = b.find_element_by_xpath('./../../..')
                account_name = list_item.text.split('\n')[0]
                followers.append(account_name)
        logger.debug('Found {} followers'.format(len(followers)))
        return followers

    def get_latest_post(self):
        """Like the latest post if not already liked"""
        # First locate the post
        logger.debug('Locating post')
        images = self.driver.find_elements_by_tag_name('img')
        posts = []
        for img in images:
            if 'px' in img.get_property('sizes'):
                posts.append(img)
        if len(posts) == 0:
            logger.debug('Could not locate any posts')
            return None
        else:
            first_post = posts[0]
            parent_anchor = first_post.find_element_by_xpath('./../../..')
            # Clicking doesn't seem to work. However we can access the href
            href = parent_anchor.get_property('href')
            # Open the image
            logger.debug('Found post with url {}, going there'.format(href))
            self.driver.get(href)
            self.short_wait()
            # An object corresponding to the actions
            # we can do with this post
            post_page = PostPage(self.driver)
            return post_page


class PostPage(_InstaPage):

    def like_current(self):
        # Locate the like button, this is tricky...
        logger.debug('Searching for like button...')
        spans = self.driver.find_elements_by_tag_name('span')
        like_spans = []
        for span in spans:
            aria_label = span.get_attribute('aria-label')
            # Sort out all spans which correspond to like-hearts
            if aria_label is None:
                continue
            if 'Like' in aria_label or 'Unlike' in aria_label:
                like_spans.append(span)
        for span in like_spans:
            # Find the one with size 24, this is the one we want
            if span.size['height'] == 24:
                status = span.get_attribute('aria-label')
                if status == 'Unlike':
                    logger.info('Picture already liked, skipping')
                elif status == 'Like':
                    logger.info('Liking picture')
                    like_button = span.find_element_by_xpath('./..')
                    logger.debug('Found like button, clicking...')
                    like_button.click()
                    self.short_wait()

    def get_tag(self):
        url = self.driver.current_url
        tag = url.split('/')[-2]
        return tag
