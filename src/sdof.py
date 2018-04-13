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

    
def take_screenshot(driver, path):
    driver.save_screenshot(path)
    print "captured:", path


def chrome_take_screenshot(driver, path):
    
    def send(cmd, params):
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd':cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        return response.get('value')

    def evaluate(script):
        response = send('Runtime.evaluate', {'returnByValue': True, 'expression': script})
        return response['result']['value']

    metrics = evaluate( \
        "({" + \
        "width: Math.max(window.innerWidth, document.body.scrollWidth, document.documentElement.scrollWidth)|0," + \
        "height: Math.max(innerHeight, document.body.scrollHeight, document.documentElement.scrollHeight)|0," + \
        "deviceScaleFactor: window.devicePixelRatio || 1," + \
        "mobile: typeof window.orientation !== 'undefined'" + \
        "})")
    send('Emulation.setDeviceMetricsOverride', metrics)
    screenshot = send('Page.captureScreenshot', {'format': 'png', 'fromSurface': True})
    send('Emulation.clearDeviceMetricsOverride', {})

    #return base64.b64decode(screenshot['data'])

    png = base64.b64decode(screenshot['data'])

    with open(r"{}".format(path), 'wb') as f:
        f.write(png)


def equal(im1, im2):
    try:
        image1 = Image.open(im1)
        print
        print "Opened {} for comparision".format(im1)
        image2 = Image.open(im2)
        print
        print "Opened {} for comparision".format(im2)
        return ImageChops.difference(image1, image2).getbbox() is None
    except IOError as e:
        print
        print "failed to compare:", e
        print im1
        print im2

def make_testrun_dir(browser, now):
    print ""
    print "making test run directory..."
    try: 
        os.makedirs("test_runs/{}/{}".format(browser, now))
    except OSError:
        if not os.path.isdir("test_runs/{}/{}".format(browser, now)):
            raise

def get_links(driver, base_url):
    """ returns a list of links scrapped from a page """
    links = []
    print "...scrapping links..."
    get_url(driver, base_url)
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        url = elem.get_attribute("href")
        if 'http' not in url:
            url = base_url + url
        links.append(url)
    print "found {} links".format(len(elems))
    return links

def get_url(driver, go_url):
    try:
        driver.get(go_url)
        print "open:", go_url
    except:
        print "Failed to open", go_url


"""
image2 = "../test/test_runs/chrome/20180315103853/TimeRangeWindow__Basic_Range_Window,_range_more_than_one_year_apart.png"
image1 = "../test/base_images/chrome/TimeRangeWindow__Basic_Range_Window,_range_more_than_one_year_apart/TimeRangeWindow__Basic_Range_Window,_range_more_than_one_year_apart.png"
result = equal(image1, image2)
print result
"""