import os
from utils import www
from utils.cache import cache

from lk_textbooks._constants import CACHE_NAME, CACHE_TIMEOUT
from lk_textbooks._utils import log

METADATA_URL = (
    'https://raw.githubusercontent.com'
    + '/nuuuwan/lk_textbooks/data/lk_textbooks.tsv'
)

@cache(CACHE_NAME, CACHE_TIMEOUT)
def get_metadata():
    data_list = www.read_tsv(METADATA_URL)
    n_data_list = len(data_list)
    log.info(f'Loaded {n_data_list} entries from {METADATA_URL}')
    return data_list

def download():
    metadata = get_metadata()
    dir_download = '/tmp/lk_textbooks/downloads'
    os.system(f'rm -rf {dir_download}')
    os.system(f'mkdir -p {dir_download}')

    index_entries = {}
    for data in metadata:
        lang = data['lang']
        grade = data['grade']
        book_name = data['book_name']

        if lang not in index_entries:
            index_entries[lang] = {}
        if grade not in index_entries[lang]:
            index_entries[lang][grade] = {}
        if book_name not in index_entries[lang][grade]:
            index_entries[lang][grade][book_name] = []

        index_entries[lang][grade][book_name].append(data)


    for lang, lang_entries in index_entries.items():
        dir_lang = f'{dir_download}/{lang}'
        os.system(f'mkdir "{dir_lang}"')
        for grade, grade_entries in lang_entries.items():
            dir_grade = f'{dir_lang}/{grade}'
            os.system(f'mkdir "{dir_grade}"')
            for book, book_entries in grade_entries.items():
                dir_book = f'{dir_grade}/{book}'
                os.system(f'mkdir "{dir_book}"')
                for data in book_entries:
                    link = data['link']
                    chapter_name = data['chapter_name']
                    # os.system(f'wget "{link}" > "{chapter_name}.pdf"')
                    os.system(f'echo "" > "{chapter_name}.pdf"')


if __name__ == '__main__':
    download()
