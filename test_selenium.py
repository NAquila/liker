import selenium
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options


def main():
    print('Starting test...')
    options = Options()
    options.headless = True
    driver = Firefox(options=options)
    print('Driver created, loading page...')
    driver.get('https://duckduckgo.com/')
    print(f'Page title is: {driver.title}')


if __name__ == '__main__':
    main()
