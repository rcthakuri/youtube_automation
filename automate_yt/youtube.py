# Scraping and Automation Lib
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from youtubesearchpython import VideosSearch
from play_keyword import PlayKeyword

# Other system LIb
import time, datetime
import warnings
import os
import threading

warnings.filterwarnings("ignore")

os.environ['WDM_LOG_LEVEL'] = '0'  # Supress Web Manager Log

# CONSTANT
YOUTUBE_URL = 'https://www.youtube.com/'
GOOGLE_CHROME_PROFILE_DIR = ''


class Youtube:
    def __init__(self, executable_path=None):
        self.driver = None
        self.video_keyword = None
        self.duration = None
        self.youtube_element_finder = None
        self.yt_play_duration = None
        self.yt_play_remaining_duration = None
        self.thread_runner = ThreadRunner()
        self.executable_path = executable_path
        self.yt_play_keyword_cls = PlayKeyword()
        self.yt_play_keyword_cls.shuffle_keyword_list()
        self.yt_play_keyword = self.yt_play_keyword_cls.keyword

    @staticmethod
    def selenium_cmd_handler(selenium_cmd, args):
        try:
            selenium_cmd(args)
        except Exception as e:
            print('Selenium Exception =>', e)

    def wait_until_id_element_presence(self, delay, element_id) -> \
            'element or False':
        try:
            element = WebDriverWait(self.driver, delay). \
                until(
                ec.presence_of_element_located(
                    (By.ID, element_id)))
            return element
        except TimeoutException:
            return False

    def start_yt_webdriver(self):
        chrome_options = Options()
        # TOGGLE COMMENT FOR headless or !headless
        # chrome_options.add_argument("--headless")

        chrome_options.add_argument('log-level=3')
        if GOOGLE_CHROME_PROFILE_DIR:
            chrome_options.add_argument(r'user-data-dir='+GOOGLE_CHROME_PROFILE_DIR)

        webdriver_params = {
            'options': chrome_options
        }

        self.driver = webdriver.Chrome(ChromeDriverManager().install(),
                                       **webdriver_params)
        self.driver.maximize_window()
        self.youtube_element_finder = YoutubeUIFinder(self.driver)

    def __del__(self):
        self.thread_runner.stop_thread()  # stop if any thread active
        if self.driver:
            self.driver.quit()

    def stop(self):
        self.__del__()
        self.driver = None

    def set_video_keyword(self, video_keyword):
        self.video_keyword = video_keyword

    def search(self):
        result = VideosSearch(self.video_keyword).result()['result'][0]['link']
        return result

    def play_yt_video(self):
        def timer():
            t_end = time.time() + self.duration
            while time.time() < t_end:
                continue
            else:
                self.stop()

        # # Clearing any previous instance
        # if self.driver:
        #     self.stop()

        th1 = self.thread_runner.Thread(target=self.play)
        th2 = self.thread_runner.Thread(target=timer)
        th3 = self.thread_runner.Thread(target=self.update_remaining_play_duration)
        th1.start()
        th2.start()
        th3.start()

    def play(self):
        try:
            if not self.driver:
                self.start_yt_webdriver()

            def start_play():
                yt_watch_video_url = self.search()
                self.driver.get(yt_watch_video_url)
                play_button = self.youtube_element_finder.get_youtube_search_button()

                if play_button and play_button.is_displayed():
                    play_button.click()
                    yt_play_duration_str = self.youtube_element_finder \
                        .get_youtube_play_duration()
                    self.yt_play_duration = self.get_duration_yt_time(yt_play_duration_str)

            start_play()

            while True:
                if self.yt_play_remaining_duration == 0.0:
                    print("Playing next video...")
                    if len(self.yt_play_keyword) == 0:
                        self.yt_play_keyword_cls.shuffle_keyword_list()
                        self.yt_play_keyword = self.yt_play_keyword_cls.keyword
                    self.set_video_keyword(video_keyword=self.yt_play_keyword[0])
                    start_play()

        except Exception as e:
            # pass
            print("\t\tError => Exception on play()", e)  # Toogle comment to see exception

    def update_remaining_play_duration(self):
        while True:
            self.yt_play_remaining_duration = self.yt_play_duration
            if isinstance(self.yt_play_remaining_duration, float) and self.yt_play_remaining_duration > 0:
                while self.yt_play_remaining_duration != 0:
                    time.sleep(1)
                    self.yt_play_remaining_duration -= 1
                    print(self.yt_play_remaining_duration)
                else:
                    self.yt_play_duration = 0
                    self.yt_play_keyword.pop(0)
                    print('Finished playing !')

    def set_duration(self, hours=None, minutes=None, second=None):
        seconds = 0
        if hours:
            seconds += hours * 60 * 60
        if minutes:
            seconds += minutes * 60
        if second:
            seconds += second

        duration = seconds
        self.duration = duration

    @staticmethod
    def get_duration_yt_time(yt_play_time_str: str) -> 'seconds':
        duration = time.strptime(yt_play_time_str, '%M:%S')
        duration = datetime.timedelta(
            minutes=duration.tm_min,
            seconds=duration.tm_sec) \
            .total_seconds()
        return duration


''' 
YOUTUBE UI SELECTOR FOR SELENIUM 
'''
# ID SELECTOR
YT_SEL_SEARCH_ID = 'search'

# XPATH SELECTOR
YT_PLAY_BUTTON_XPATH = f'''
                        //button[@aria-label="Play"]
                        '''
YT_PLAY_DURATION_XPATH = f'''
                        //span[@class='ytp-time-duration']
                        '''


class YoutubeUIFinder:
    def __init__(self, driver: 'Selenium Webdriver object'):
        self.webdriver = driver

    def get_youtube_search(self) -> 'Webdriver element':
        yt_search = self.webdriver \
            .find_element_by_id('search-input') \
            .find_element_by_id(YT_SEL_SEARCH_ID)
        return yt_search

    def get_youtube_search_button(self) -> 'Webdriver element':
        yt_search_btn = WebDriverWait(self.webdriver, 10) \
            .until(
            ec.element_to_be_clickable(
                (By.XPATH, YT_PLAY_BUTTON_XPATH)))

        return yt_search_btn

    def get_youtube_play_duration(self) -> 'Duration in str':
        yt_play_duration = self.webdriver \
            .find_elements_by_xpath(YT_PLAY_DURATION_XPATH)[0] \
            .text
        return yt_play_duration


class ThreadRunner(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(ThreadRunner, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.Thread = threading.Thread

    def stop_thread(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def main():
    yt = Youtube()
    while True:
        cli_menu(yt)


cli_menu_options = '''
    1. Play/Next [With Input]
    2. Play/Next [With Keyword]
    3. Stop 
    4. Quit
            '''


def cli_menu(yt: 'Youtube Object'):
    def set_play_requirement(user_keyword_input=False):
        d = float(input("\tEnter hours to play: "))
        if user_keyword_input:
            k = input("\tEnter play keyword: ")
        else:
            k = yt.yt_play_keyword[0]
            time.sleep(10)
        yt.set_duration(d)
        yt.set_video_keyword(k)

    def menu():
        if user_input == 1:
            set_play_requirement(user_keyword_input=True)
            yt.play_yt_video()
        elif user_input == 2:
            set_play_requirement()
            yt.play_yt_video()
        elif user_input == 3:
            if yt.driver:
                yt.stop()
            else:
                print("\t\tInfo => Player has not started yet")
        elif user_input == 4:
            exit()
        else:
            print("\t\tWrong input!!")

    print(cli_menu_options)

    try:
        user_input = int(input('\tEnter your choice: '))
        menu()
    except Exception as e:
        print('\t\tError => ', e)


if __name__ == '__main__':
    main()
