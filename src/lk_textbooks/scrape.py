import argparse
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.firefox.options import Options
from utils import tsv
from utils.cache import cache

from lk_textbooks._constants import CACHE_NAME, CACHE_TIMEOUT
from lk_textbooks._utils import log

URL = 'http://www.edupub.gov.lk/BooksDownload.php'
NEW_PAGE_SLEEP_TIME = 1


@cache(CACHE_NAME, CACHE_TIMEOUT)
def scrape_get_langs_and_grades():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(URL)

    select_lang = driver.find_element_by_id('BookLanguage')
    langs = []
    for option in select_lang.find_elements_by_tag_name('option'):
        if 'Select' not in option.text:
            langs.append(option.text)

    select_lang = driver.find_element_by_id('BookGrade')
    grades = []
    for option in select_lang.find_elements_by_tag_name('option'):
        if 'Select' not in option.text:
            grades.append(option.text)

    driver.quit()
    return langs, grades


@cache(CACHE_NAME, CACHE_TIMEOUT)
def scrape_get_book_names(lang, grade):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(URL)

    select_lang = driver.find_element_by_id('BookLanguage')
    for option in select_lang.find_elements_by_tag_name('option'):
        if option.text == lang:
            option.click()

    select_lang = driver.find_element_by_id('BookGrade')
    for option in select_lang.find_elements_by_tag_name('option'):
        if option.text == grade:
            option.click()

    input_submit = driver.find_element_by_class_name('TextbookSubmitButton')
    input_submit.click()

    time.sleep(NEW_PAGE_SLEEP_TIME)
    book_names = []
    for a in driver.find_elements_by_class_name('SelectSyllabuss'):
        book_names.append(a.text)

    driver.quit()
    return book_names


@cache(CACHE_NAME, CACHE_TIMEOUT)
def scrape_get_chapter_links(lang, grade, book_name):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(URL)

    select_lang = driver.find_element_by_id('BookLanguage')
    for option in select_lang.find_elements_by_tag_name('option'):
        if option.text == lang:
            option.click()

    select_lang = driver.find_element_by_id('BookGrade')
    for option in select_lang.find_elements_by_tag_name('option'):
        if option.text == grade:
            option.click()

    input_submit = driver.find_element_by_class_name('TextbookSubmitButton')
    input_submit.click()

    time.sleep(NEW_PAGE_SLEEP_TIME)

    for a in driver.find_elements_by_class_name('SelectSyllabuss'):
        if a.text == book_name:
            a.click()

    time.sleep(NEW_PAGE_SLEEP_TIME)

    chapter_links = []
    for a in driver.find_elements_by_class_name('SelectChapter'):
        chapter_links.append(
            dict(
                url=a.get_attribute('href'),
                name=a.text,
            )
        )
    driver.quit()
    return chapter_links


def scrape_all(limit):
    log.info(f'limit = {limit}')
    langs, grades = scrape_get_langs_and_grades()
    n_langs, n_grades = len(langs), len(grades)
    log.info(f'Got {n_langs} Languages and {n_grades} Grades.')
    data_list = []
    is_over_limit = False
    for lang in langs:
        for grade in grades:

            try:
                book_names = scrape_get_book_names(lang, grade)
            except StaleElementReferenceException:
                book_names = []

            n_book_names = len(book_names)
            log.info(f'Got {n_book_names} books for {lang}/{grade}')
            for book_name in book_names:
                try:
                    chapter_links = scrape_get_chapter_links(
                        lang, grade, book_name
                    )
                except StaleElementReferenceException:
                    chapter_links = []

                n_chapter_links = len(chapter_links)
                log.info(
                    f'Got {n_chapter_links} chapters '
                    + f'for {lang}/{grade}/{book_name}'
                )
                for chapter_link in chapter_links:
                    data_list.append(
                        dict(
                            lang=lang,
                            grade=grade,
                            book_name=book_name,
                            chapter_name=chapter_link['name'],
                            link=chapter_link['url'],
                        )
                    )
                    if len(data_list) >= limit:
                        is_over_limit = True
                        break

                if is_over_limit:
                    break
            if is_over_limit:
                break
        if is_over_limit:
            break

    data_file = '/tmp/lk_textbooks.tsv'
    tsv.write(data_file, data_list)
    n_data_list = len(data_list)
    log.info(f'Saved {n_data_list} entries to {data_file}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--limit',
        help='Maxiumum entries to scrape',
        type=int,
        default=10000,
    )
    args = parser.parse_args()
    scrape_all(args.limit)
