# image compare with pillow

import sys
from selenium import webdriver
import os
import time
import datetime
import json
import base64
from PIL import ImageChops
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def take_screenshot(driver, path):
    driver.save_screenshot(path)
    logging.info(f"Captured: {path}")


def chrome_take_screenshot(driver, path):
    def evaluate(script):
        result = driver.execute_cdp_cmd('Runtime.evaluate', {'returnByValue': True, 'expression': script})
        return result['result']['value']

    metrics = evaluate(
        "({" +
        "width: Math.max(window.innerWidth, document.body.scrollWidth, document.documentElement.scrollWidth)|0," +
        "height: Math.max(innerHeight, document.body.scrollHeight, document.documentElement.scrollHeight)|0," +
        "deviceScaleFactor: window.devicePixelRatio || 1," +
        "mobile: typeof window.orientation !== 'undefined'" +
        "})")
    driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', metrics)
    screenshot = driver.execute_cdp_cmd('Page.captureScreenshot', {'format': 'png', 'fromSurface': True})
    driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})

    png = base64.b64decode(screenshot['data'])

    with open(path, 'wb') as f:
        f.write(png)


def equal(im1, im2):
    try:
        image1 = Image.open(im1)
        logging.info(f"Opened {im1} for comparison")
        image2 = Image.open(im2)
        logging.info(f"Opened {im2} for comparison")
        if ImageChops.difference(image1, image2).getbbox() is None:
            logging.info(f"Images {im1} and {im2} are equal")
            return True
        else:
            logging.info(f"Images {im1} and {im2} are different")
            return False
    except IOError as e:
        logging.error(f"Failed to compare {im1} and {im2}: {e}")
        return None


def make_testrun_dir(browser, now):
    logging.info("Making test run directory...")
    try:
        os.makedirs(f"test_runs/{browser}/{now}")
        logging.info(f"Test run directory created: test_runs/{browser}/{now}")
    except OSError as e:
        if not os.path.isdir(f"test_runs/{browser}/{now}"):
            logging.error(f"Failed to create test run directory: {e}")
            raise
        else:
            logging.info(f"Test run directory already exists: test_runs/{browser}/{now}")


def get_links(driver, base_url):
    """ returns a list of links scrapped from a page """
    links = []
    logging.info("...scrapping links...")
    get_url(driver, base_url)
    elems = driver.find_elements(by='xpath', value="//a[@href]")
    for elem in elems:
        url = elem.get_attribute("href")
        if 'http' not in url:
            url = base_url + url
        links.append(url)
    logging.info(f"Found {len(elems)} links")
    return links


def get_url(driver, go_url):
    try:
        driver.get(go_url)
        logging.info(f"Opened: {go_url}")
    except Exception as e:
        logging.error(f"Failed to open {go_url}: {e}")


"""
image2 = "../test/test_runs/chrome/20180315103853/TimeRangeWindow__Basic_Range_Window,_range_more_than_one_year_apart.png"
image1 = "../test/base_images/chrome/TimeRangeWindow__Basic_Range_Window,_range_more_than_one_year_apart/TimeRangeWindow__Basic_Range_Window,_range_more_than_one_year_apart.png"
result = equal(image1, image2)
print(result)
"""