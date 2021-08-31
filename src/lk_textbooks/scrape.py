from selenium import webdriver
from selenium.webdriver.firefox.options import Options

URL = 'http://www.edupub.gov.lk/BooksDownload.php'

def scrape():
    firefox_options = Options()
    firefox_options.set_headless()

    driver = webdriver.Firefox(firefox_options=firefox_options)

    driver.get(URL)

if __name__ == '__main__':
    scrape()    
