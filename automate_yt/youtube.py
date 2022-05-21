# Scraping and Automation Lib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from youtubesearchpython import VideosSearch

# Other system LIb
import time
import warnings
import os
import threading
warnings.filterwarnings("ignore")


os.environ['WDM_LOG_LEVEL'] = '0'  # Supress Web Manager Log

# CONSTANT
YOUTUBE_URL = 'https://www.youtube.com/'


class Youtube:
    def __init__(self, executable_path=None):
        self.driver = None
        self.video_keyword = None
        self.duration = None
        self.youtube_element_finder = None
        self.thread_runner = ThreadRunner()
        self.executable_path = executable_path

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

        th1.start()
        th2.start()

    def play(self):
        try:
            if not self.driver:
                self.start_yt_webdriver()

            yt_watch_video_url = self.search()
            self.driver.get(yt_watch_video_url)
            play_button = self.youtube_element_finder.get_youtube_search_button()

            if play_button and play_button.is_displayed():
                play_button.click()

        except Exception:
            pass
            # print("\t\tError => Exception on play()") # Toogle comment to see exception

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


''' 
YOUTUBE UI SELECTOR FOR SELENIUM 
'''
# ID SELECTOR
YT_SEL_SEARCH_ID = 'search'

# ATTRIBUTE SELECTOR
YT_PLAY_BUTTON_XPATH = f'''
                        //button[@aria-label="Play"]
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
        yt_search_btn = WebDriverWait(self.webdriver, 10)\
            .until(
                ec.element_to_be_clickable(
                    (By.XPATH, YT_PLAY_BUTTON_XPATH)))

        return yt_search_btn


class ThreadRunner(threading.Thread):

    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""
    def __init__(self,  *args, **kwargs):
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
    1. Play/Next
    2. Stop 
    3. Quit
            '''


def cli_menu(yt: 'Youtube Object'):
    def set_play_requirement():
        d = float(input("\tEnter hours to play: "))
        k = input("\tEnter play keyword: ")
        yt.set_duration(d)
        yt.set_video_keyword(k)

    def menu():
        if user_input == 1:
            set_play_requirement()
            yt.play_yt_video()
        elif user_input == 2:
            if yt.driver:
                yt.stop()
            else:
                print("\t\tInfo => Player has not started yet")
        elif user_input == 3:
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
