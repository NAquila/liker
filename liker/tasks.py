import luigi
from datetime import datetime, timedelta
import os
import logging
import selenium
from selenium.webdriver.firefox.options import Options
from insta_pages import LogInPage, ProfilePage
from pymongo import MongoClient
import json
import random
import time

logger = logging.getLogger(__name__)


class _ProfileBase(luigi.Task):
    """Mixin-class to perform all instagram-profile jobs"""
    credentials_file = luigi.Parameter()
    profile = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(_ProfileBase, self).__init__(*args, **kwargs)
        # Get a connection to the db
        self.db_connection = MongoClient().insta_bot
        

    def wait(self):
        wait_base = 0.5
        noise = random.expovariate(1/wait_base)
        actual_wait = wait_base + noise
        logger.debug(f'Waiting {1000*wait_base}ms')
        time.sleep(actual_wait)

    def get_profile_doc(self):
        """Return the document that has information about this profile.
        If no such document exists, returns None"""
        profile_doc = (self.db_connection.accounts
                       .find_one({'profile_name':self.profile}))
        return profile_doc

    def get_new_driver(self):
        options = Options()
        options.headless = False
        return selenium.webdriver.Firefox(options=options)

    def set_profile_page(self, driver):
        self.profile_page = ProfilePage(driver=driver,
                                        profile=self.profile)

    def log_in(self, driver):
        # Read credentials from file
        with open(self.credentials_file, 'r') as f:
            self.credentials = json.load(f)
        # Goto homepage
        driver.get('https://www.instagram.com')
        self.wait()
        # Log in
        page = LogInPage(driver)
        page.log_in(self.credentials)

    def log_in_and_goto_profile(self):
        driver = self.get_new_driver()
        self.log_in(driver)
        self.wait()
        self.set_profile_page(driver)
        self.profile_page.goto_url()
        self.wait()

    def close(self):
        if hasattr(self, 'profile_page'):
            logger.debug('Closing driver')
            self.profile_page.close()
        else:
            logger.debug("Task has no profile page, ignoring close command") 


class GetFollowers(_ProfileBase):
    """Task that reads the followers of a profile.
    """

    def run(self):
        self.log_in_and_goto_profile()
        # Read followers
        followers = self.profile_page.get_followers()
        # Store in db
        account_docs = self.db_connection.accounts
        account_docs.update_one({'profile_name': self.profile},
                                {'$set':
                                 {'followers': {'value': followers,
                                                'time_inserted':
                                                datetime.now()}}},
                                upsert=True)
        self.close()

    def complete(self):
        profile_doc = self.get_profile_doc()
        if profile_doc is None:
            return False
        elif 'followers' not in profile_doc.keys():
            return False
        else:  # Document and entry in document exists, good enough for now
            return True

    def get_followers(self):
        if not self.complete():
            raise TypeError('Only call get_followers-function when'
                            ' task is complete')
        profile_doc = self.get_profile_doc()
        return profile_doc['followers']['value']
                


class FollowProfile(_ProfileBase):
    """Task that follows a profile"""

    def run(self):
        self.log_in_and_goto_profile()
        self.profile_page.follow()
        # Insert new status in db
        self.wait()
        new_status = self.profile_page.get_follow_status()
        account_docs = self.db_connection.accounts
        account_docs.update_one({'profile_name': self.profile},
                                {'$set':
                                 {'status': {'value': new_status,
                                             'time_inserted':
                                             datetime.now()}}},
                                upsert=True)
        self.close()

    def complete(self):
        # Task is complete if we have requested to follow/follow this profile
        profile_doc = self.get_profile_doc()
        if profile_doc is None:
            return False
        elif 'status' not in profile_doc.keys():
            return False
        else:
            status = profile_doc['status']['value']
            print(f'follow_task sees {status}')
            return status in ('Following', 'Requested')


class UnfollowProfile(_ProfileBase):
    """Task that follows a profile"""

    def run(self):
        self.log_in_and_goto_profile()
        self.profile_page.unfollow()
        # Insert new status in db
        self.wait()
        new_status = self.profile_page.get_follow_status()
        account_docs = self.db_connection.accounts
        account_docs.update_one({'profile_name': self.profile},
                                {'$set':
                                 {'status': {'value': new_status,
                                             'time_inserted': datetime.now()}}},
                                upsert=True)
        self.close()

    def complete(self):
        profile_doc = self.get_profile_doc()
        if profile_doc is None:
            return False
        elif 'status' not in profile_doc.keys():
            return False
        else:
            status = profile_doc['status']['value']
            # Task is complete if we have the ability to follow this profile
            print(f'unfollow_task sees {status}')
            return status == 'Follow'

class LikeLatest(_ProfileBase):

    def run(self):
        self.log_in_and_goto_profile()
        latest_post_page = self.profile_page.get_latest_post()
        latest_post_page.like_current()
        post_tag = latest_post_page.get_tag()
        account_docs = self.db_connection.accounts
        account_docs.update_one({'profile_name': self.profile},
                                {'$set':
                                 {'latest_post': {'tag': post_tag,
                                                  'time_liked': datetime.now()}}},
                                upsert=True)
        self.wait()
        self.close()

    def complete(self):
        profile_doc = self.get_profile_doc()
        if profile_doc is None:
            return False
        elif 'latest_post' not in profile_doc.keys():
            return False
        else:
            timeout = timedelta(days=7)
            last_liked = profile_doc['latest_post']['time_liked']
            expired = (datetime.now() - last_liked) > timeout
            return not expired
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    profile = 'juliakbrou'
    luigi.build([GetFollowers(profile=profile)], local_scheduler=True)
