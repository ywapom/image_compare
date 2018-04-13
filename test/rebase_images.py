import sys
import os
import time
import datetime
import argparse
sys.path.append("..")
import src.sdof
from shutil import move
from selenium import webdriver


class RebaseImages():

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
    def __init__(self, env='tst', browser='chrome'):
        self.env = env
        self.browser = browser

        if browser == "chrome":
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Firefox()
        
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
        s = s.replace('https://','')
        s = s.replace('http://','')
        s = s.replace('#','_')
        s = s.replace('www.','')
        s = s.replace('.com','')
        s = s.replace('/','_')
        return s

    def move_images(self, screen_names):
        """ replaces base images with newly captured images """
        for t_name in enumerate(screen_names):
            name = t_name[1]
            try:
                if not os.path.exists("../test/base_images/{}/{}".format(self.browser, name)):
                    os.makedirs("../test/base_images/{}/{}".format(self.browser, name))
                    print "created base folder: {}".format(name)
                os.rename("{}.png".format(name), "../test/base_images/{}/{}/{}.png".format(self.browser, name, name))
                print "re-based: {}".format(name)
            except OSError as e:
                print "Failed to move image capture: {}".format(name), e
        

    def capture_screens(self, links):
        for link in links:
            self.get_url(link[1])
            fname = "{}.png".format(self.get_name(link[1]))
            time.sleep(2)
            src.sdof.take_screenshot(self.driver, fname)
        self.driver.close()

    def capture_screens_chrome(self, links):
        for link in enumerate(links):
            self.get_url(link[1])
            print  "link: ", link[1]
            fname = "{}.png".format(self.get_name(link[1]))
            time.sleep(2)
            src.sdof.chrome_take_screenshot(self.driver, fname)
        self.driver.close()
    
    def get_url(self, go_url):
        try:
            self.driver.get(go_url)
            print "open:", go_url
        except:
            print "Failed to open", go_url


def main():
    arg_parser = argparse.ArgumentParser(description='Perform react card image compare against an environment and browser')
    arg_parser.add_argument('--browser', help='Browser name: chrome, firefox, support for others tbd', action='store', default='chrome')
    arg_parser.add_argument('--env', help='Environment: tst, dev, or other', action='store', default='tst')
    args = arg_parser.parse_args()

    if args.browser in ['chrome', 'firefox']:
        pass
    else:
        raise('Error on browser selection')

    home_url = "https://google.com/"

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


