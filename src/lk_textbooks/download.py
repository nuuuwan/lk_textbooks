import os
import urllib.request

from utils import www
from utils.cache import cache

from lk_textbooks._constants import CACHE_NAME, CACHE_TIMEOUT
from lk_textbooks._utils import log

METADATA_URL = (
    'https://raw.githubusercontent.com'
    + '/nuuuwan/lk_textbooks/data/lk_textbooks.tsv'
)
MAX_REMOTE_FILE_SIZE_MB = 10


@cache(CACHE_NAME, CACHE_TIMEOUT)
def get_remote_file_size_mb(url):
    file = urllib.request.urlopen(url)
    return file.length / 1_000_000.0


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
                    url = data['link']
                    file_size_mb = get_remote_file_size_mb(url)
                    chapter_id = data['chapter_id']


                    if file_size_mb < MAX_REMOTE_FILE_SIZE_MB:
                        chapter_file = f'{dir_book}/{chapter_id}.pdf'
                        if not os.path.exists(chapter_file):
                            os.system(f'wget "{url}" -o {chapter_file}')
                            log.info(f'Downloaded {chapter_file} ({file_size_mb:.1f}MB)')
                        else:
                            log.warning(f'{chapter_file} exists')

                    else:
                        chapter_file = f'{dir_book}/{chapter_id}.pdf.dummy'
                        os.system(f'echo "" > {chapter_file}')
                        log.warning(
                            f'Dummy Downloaded {chapter_file} '
                            + f'({file_size_mb:.1f}MB) - Too Big'
                        )


if __name__ == '__main__':
    download()
