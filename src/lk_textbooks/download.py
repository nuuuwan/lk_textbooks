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
        lang_id = data['lang_id']
        grade_id = data['grade_id']
        book_id = data['book_id']

        if lang_id not in index_entries:
            index_entries[lang_id] = {}
        if grade_id not in index_entries[lang_id]:
            index_entries[lang_id][grade_id] = {}
        if book_id not in index_entries[lang_id][grade_id]:
            index_entries[lang_id][grade_id][book_id] = []

        index_entries[lang_id][grade_id][book_id].append(data)

    for lang_id, lang_entries in index_entries.items():
        dir_lang = f'{dir_download}/{lang_id}'
        os.system(f'mkdir {dir_lang}')
        for grade_id, grade_entries in lang_entries.items():
            dir_grade = f'{dir_lang}/{grade_id}'
            os.system(f'mkdir {dir_grade}')
            for book_id, book_entries in grade_entries.items():
                dir_book = f'{dir_grade}/{book_id}'
                os.system(f'mkdir {dir_book}')
                for data in book_entries:
                    data['link']
                    chapter_id = data['chapter_id']
                    chapter_file = f'{dir_book}/{chapter_id}.pdf'
                    os.system(f'wget "{link}" > {chapter_file}')
                    log.info(f'Downloaded {chapter_file}')


if __name__ == '__main__':
    download()
