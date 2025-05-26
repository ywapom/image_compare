import sys
import os
import datetime
import argparse
sys.path.append("..")
# Append the current working directory to sys.path
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import src.sdof
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class RebaseImages:

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def __init__(self, env='tst', browser='chrome'):
        self.env = env
        self.browser = browser

        if browser == "chrome":
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Firefox()

        self.wait = WebDriverWait(self.driver, 10)  # Initialize WebDriverWait
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    def get_names(self, links):
        names = []
        for link in links:
            s = self.get_name(link)
            names.append(s)
        return names

    def get_name(self, link):
        s = ''.join(link)
        if '?' in s:
            k = s.split('?')
            s = k[0]
        if 'javascript' in s:
            m = s.split('javascript')
            s = m[0]
        s = s.replace('https://', '')
        s = s.replace('http://', '')
        s = s.replace('#', '_')
        s = s.replace('www.', '')
        s = s.replace('.com', '')
        s = s.replace('/', '_')
        return s

    def move_images(self, screen_names):
        """ replaces base images with newly captured images """
        for t_name in enumerate(screen_names):
            name = t_name[1]
            try:
                base_dir = os.path.join("..", "test", "base_images", self.browser, name)
                if not os.path.exists(base_dir):
                    os.makedirs(base_dir)
                    print(f"created base folder: {name}")
                old_path = f"{name}.png"
                new_path = os.path.join("..", "test", "base_images", self.browser, name, f"{name}.png")
                os.rename(old_path, new_path)
                print(f"re-based: {name}")
            except OSError as e:
                print(f"Failed to move image capture: {name}", e)

    def capture_screens(self, links):
        for link in links:
            self.get_url(link[1])
            fname = f"{self.get_name(link[1])}.png"
            self.wait_for_page_load()  # Use explicit wait
            src.sdof.take_screenshot(self.driver, fname)
        self.driver.close()

    def capture_screens_chrome(self, links):
        for link in enumerate(links):
            self.get_url(link[1])
            print("link: ", link[1])
            fname = f"{self.get_name(link[1])}.png"
            self.wait_for_page_load()  # Use explicit wait
            src.sdof.chrome_take_screenshot(self.driver, fname)
        self.driver.close()

    def get_url(self, go_url):
        try:
            self.driver.get(go_url)
            print("open:", go_url)
        except Exception as e:
            print("Failed to open", go_url)

    def wait_for_page_load(self, timeout=10):
            """Waits for the page to be fully loaded."""
            try:
                self.wait.until(
                    EC.presence_of_element_located(('tag name', 'body'))
                )
                # Optional: Add a short sleep if the above isn't sufficient in some cases
                # time.sleep(0.5)
            except TimeoutException:
                print("Page load timed out.")


def main():
    arg_parser = argparse.ArgumentParser(description='Perform react card image compare against an environment and browser')
    arg_parser.add_argument('--browser', help='Browser name: chrome, firefox, support for others tbd', action='store', default='chrome')
    arg_parser.add_argument('--env', help='Environment: tst, dev, or other', action='store', default='tst')
    args = arg_parser.parse_args()

    if args.browser in ['chrome', 'firefox']:
        pass
    else:
        raise ValueError('Error on browser selection')

    home_url = "https://quantum-embrace.com/"

    my_test = RebaseImages(args.env, args.browser)
    links = src.sdof.get_links(my_test.driver, home_url)
    names = my_test.get_names(links)

    if my_test.browser == 'chrome':
        my_test.capture_screens_chrome(links)
    else:
        my_test.capture_screens(links)
    my_test.move_images(names)

if __name__ == "__main__":
    main()