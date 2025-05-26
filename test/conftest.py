import pytest
import datetime
from selenium import webdriver

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--env", action="store", default="tst")

@pytest.fixture
def browser_name(request):
    browser = request.config.getoption("--browser")
    return browser

@pytest.fixture
def my_driver(request):
    browser = request.config.getoption("--browser")
    if browser == "chrome":
        driver = webdriver.Chrome()
        yield driver
        driver.quit()
    elif browser == "firefox":
        driver = webdriver.Firefox()
        yield driver
        #driver.quit()
    elif browser == "IE":
        driver = webdriver.ie.driver()
        yield driver
        driver.quit()
    elif browser == "headless":
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=options)
    else:
        driver = webdriver.Firefox()
        yield driver
        driver.quit()


@pytest.fixture
def my_env(request):
    env = request.config.getoption("--env")
    return env


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.browser
    if 'browser' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("browser", [option_value])
    option_value = metafunc.config.option.env
    if 'env' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("env", [option_value])


    