import random
import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from config import Config, get_executable_dir
from triage.User import User
import json
from datetime import datetime
from selenium import webdriver


# Function to convert epoch time to human-readable format
def epoch_to_datetime(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')


class XActions:

    def __init__(self, config: Config):
        self._driver = None
        self.multi_message_mode = False
        self.config = config

    @property
    def driver(self):
        if self._driver is None:
            options = webdriver.ChromeOptions()
            self._driver = webdriver.Chrome(options=options)
        return self._driver

    def save_cookies_until_auth_token(self):
        cookies = self.driver.get_cookies()
        while 'auth_token' not in str(cookies):
            time.sleep(1)
            cookies = self.driver.get_cookies()
        with open(get_executable_dir() / 'cookies.txt', 'w') as file:
            json.dump(cookies, file)

    def login(self):
        self.driver.get('https://x.com')
        should_use_cookies = True
        current_time = datetime.now().timestamp()
        try:
            with open(get_executable_dir() / 'cookies.txt', 'r') as file:
                cookies = json.load(file)
                for cookie in cookies:
                    if 'expiry' in cookie and 'auth_token' in cookie:
                        expiry_time = cookie['expiry']
                        expiry_date = epoch_to_datetime(expiry_time)
                        print(f"Cookie {cookie['name']} expires on: {expiry_date}")
                        # Check if the cookie is expiring within 24 hours (86400 seconds)
                        if expiry_time - current_time <= 86400:  # 86400 seconds = 24 hours
                            should_use_cookies = False
                            break
        except Exception as e:
            # Just means we don't have a cookies.txt file yet.
            print("No existing cookies file... Expect to receive an Unexpected log in notification", e)
            should_use_cookies = False
            pass

        if should_use_cookies:
            self.driver.delete_all_cookies()

            # Load cookies from file
            with open(get_executable_dir() / 'cookies.txt', 'r') as file:
                cookies = json.load(file)

            # Add each cookie back to the browser
            for cookie in cookies:
                self.driver.add_cookie(cookie)

            self.driver.refresh()
            return True

        self.driver.get('https://x.com/login')

    def scrape_user_name(self, name):
        self.driver.get(f"https://x.com/{name}/verified_followers")
        gathered_verified = []

        def gather_users():
            followers = find_x_path(self.driver, "//*[@id=\"react-root\"]/div/div/div[2]/main/div/div/div/div/div/section/div/div")
            if followers is None:
                return
            lines = str(followers.text).split('\n')
            for l in range(0, len(lines)):
                if lines[l] != "Follow":
                    continue
                try:
                    username = lines[l-1]
                    display_name = lines[l-2]
                    bio = ""
                    if len(lines) >= l+1:
                        bio = lines[l+1]
                    if not any(user.username == username for user in gathered_verified):
                        gathered_verified.append(User(display_name, username, sourced_from=name, bio=bio))
                except Exception as e:
                    continue

        # Scroll in small increments
        scroll_pause_time = 1  # Adjust this for speed
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        current_scroll = 0
        scroll_increment = 500  # Set the scroll amount per increment

        while current_scroll < scroll_height:
            self.driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_increment)
            current_scroll += scroll_increment
            time.sleep(scroll_pause_time)
            # Update scroll height if content loads dynamically
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            gather_users()
            if len(gathered_verified) == 0:
                return []
        return gathered_verified

    def dm_user(self, user):
        self.driver.get("https://x.com/" + str(user.username.replace("@", "")))

        time.sleep(random.randrange(3, 8))
        try:
            # Locate the first <a> element with "following" in the href
            following_link = self.driver.find_element(By.CSS_SELECTOR, "a[href*='following']")

            # Locate the first <span> child of the <a> tag
            following_span_child = following_link.find_element(By.TAG_NAME, "span")

            print("following", following_span_child.text)
            user.following = convert_following_text_to_int(following_span_child.text)

            # Locate the first <a> element with "following" in the href
            followers_link = self.driver.find_element(By.CSS_SELECTOR, "a[href*='followers']")

            # Locate the first <span> child of the <a> tag
            followers_span_child = followers_link.find_element(By.TAG_NAME, "span")

            print("followers", followers_span_child.text)
            user.followers = convert_following_text_to_int(followers_span_child.text)

            if user.followers < 50 or user.following < 50 or user.followers > 5000:
                return False

            # Locate the desired <div> element
            profile_header_items = self.driver.find_element(By.CSS_SELECTOR,"div[data-testid*='UserProfileHeader_Items']")
            user.bio += profile_header_items.text
            for excluded_keyword in self.config.exclude_keywords:
                if user.check_for_keyword(excluded_keyword):
                    print("Not DMing because has keyword, ", excluded_keyword, user.username)
                    return False

        except Exception as e:
            print("Could not find or interact with the <span> child:", str(e))

        # #like some posts
        # try:
        #     like_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Like'][role='button']")
        #     like_buttons[0].click()
        # except Exception as e:
        #     print("Error liking posts ;(")

        try:
            message_button = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Message'][role='button']")[0]
            print("found it")
            message_button.click()
        except Exception as e:
            print("Can not DM user")
            return False

        time.sleep(3)

        try:
            # Locate the div with role="textbox"

            # Example: Enter text into the contenteditable div
            name = '@' + user.username
            try:
                split_name = user.name.split(' ')
                name = str(split_name[0]).capitalize()
                if name == "The":
                    name = str(split_name[1]).capitalize()
                split_name = user.name.split('.')
                if len(split_name) > 1:
                    name = str(split_name[0]).capitalize()
                    if name == "The":
                        name = str(split_name[1]).capitalize()
            except Exception as e:
                print("Weird name:", str(e))
            message = self.config.dm_template.replace("{name}", name.replace(".", "")).split('\n')

            textbox_div = self.driver.find_element(By.CSS_SELECTOR, "div[role='textbox']")
            for m in message:
                textbox_div = self.driver.find_element(By.CSS_SELECTOR, "div[role='textbox']")
                if m == '':
                    textbox_div.send_keys(Keys.SHIFT + Keys.ENTER)
                    time.sleep(1)
                else:
                    textbox_div.send_keys(m)
                    textbox_div.send_keys(Keys.SHIFT + Keys.ENTER)
                    time.sleep(1)
            textbox_div.send_keys(Keys.ENTER)
            time.sleep(random.randrange(5, 10))
        except Exception as e:
            print("Could not find or interact with the textbox div:", str(e))
            return False

        return True

    def off(self):
        try:
            if self._driver is not None:
                self.driver.close()
        except Exception as e:
            print("Error closing driver:", str(e))
        self._driver = None

    def is_browser_closed(self):
        return self._driver is None


def convert_following_text_to_int(text: str):
    text = text.strip().upper()
    text = text.replace(",", "")
    if text.endswith('K'):
        return int(float(text[:-1]) * 1_000)
    elif text.endswith('M'):
        return int(float(text[:-1]) * 1_000_000)
    else:
        return int(text)


def find_x_path(driver, xpath):
    for i in range(0, 60):
        try:
            element = driver.find_element(By.XPATH, xpath)
            return element
        except Exception as e:
            print(i, "not found:", xpath)
            time.sleep(1)
