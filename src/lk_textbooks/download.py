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
MAX_REMOTE_FILE_SIZE_MB = 1


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
    n_metadata = len(metadata)
    dir_download = '/tmp/lk_textbooks/docs'
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

    i_metadata = 0
    for lang_id, lang_entries in index_entries.items():

        dir_lang = os.path.join(dir_download, lang_id)
        os.system(f'mkdir {dir_lang}')
        for grade_id, grade_entries in lang_entries.items():

            dir_grade = os.path.join(dir_lang, grade_id)
            os.system(f'mkdir {dir_grade}')
            for book_id, book_entries in grade_entries.items():

                dir_book = os.path.join(dir_grade, book_id)
                os.system(f'mkdir {dir_book}')
                for data in book_entries:

                    url = data['link']
                    file_size_mb = get_remote_file_size_mb(url)
                    chapter_id = data['chapter_id']
                    i_metadata += 1
                    log.info(
                        f'{i_metadata}/{n_metadata}: '
                        + f' {lang_id}{grade_id}{book_id}{chapter_id}'
                    )

                    if file_size_mb < MAX_REMOTE_FILE_SIZE_MB:
                        chapter_file = os.path.join(
                            dir_book, f'{chapter_id}.pdf'
                        )

                        if os.path.exists(chapter_file):
                            log.warning(f'{chapter_file} exists')
                        else:

                            remote_url = os.path.join(
                                'https://raw.githubusercontent.com',
                                'nuuuwan/lk_textbooks/data/downloads',
                                f'{lang_id}/{grade_id}/{book_id}',
                                f'{chapter_id}.pdf',
                            )

                            if www.exists(remote_url):
                                log.warning(f'{remote_url} exists.')
                            else:
                                os.system(f'wget -O {chapter_file} "{url}" ')
                                log.info(
                                    f'\tDownloaded {chapter_file}'
                                    + f' ({file_size_mb:.1f}MB)'
                                )

                    else:
                        chapter_file = f'{dir_book}/{chapter_id}.pdf.dummy'
                        os.system(f'echo "" > {chapter_file}')
                        log.warning(
                            f'\tDummy Downloaded {chapter_file} '
                            + f'({file_size_mb:.1f}MB) - Too Big'
                        )


if __name__ == '__main__':
    download()
