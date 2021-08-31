import os
import urllib.request

from utils import filex, timex, www
from utils.cache import cache

from lk_textbooks._constants import CACHE_NAME, CACHE_TIMEOUT
from lk_textbooks._utils import log

METADATA_URL = (
    'https://raw.githubusercontent.com'
    + '/nuuuwan/lk_textbooks/data/lk_textbooks.tsv'
)
MAX_REMOTE_FILE_SIZE_MB = 1
DIR_DOCS = '/tmp/lk_textbooks/docs'
REMOTE_DIR_DOCS = 'https://github.com/nuuuwan/lk_textbooks/tree/data/docs'

def init():
    os.system(f'rm -rf {DIR_DOCS}')
    os.system(f'mkdir -p {DIR_DOCS}')


@cache(CACHE_NAME, CACHE_TIMEOUT)
def get_remote_file_size_mb(url):
    file = urllib.request.urlopen(url)
    return file.length / 1_000_000.0


def get_metadata():
    data_list = www.read_tsv(METADATA_URL)
    n_data_list = len(data_list)
    log.info(f'Loaded {n_data_list} entries from {METADATA_URL}')
    return data_list


def get_metadata_map():
    metadata = get_metadata()
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
    return index_entries


def download():
    index_entries = get_metadata_map()


    i_metadata = 0
    for lang_id, lang_entries in index_entries.items():

        dir_lang = os.path.join(DIR_DOCS, lang_id)
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
                        f'{i_metadata}: '
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
                                REMOTE_DIR_DOCS,
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


def build_summary_md():
    index_entries = get_metadata_map()
    time_str = timex.format_time(timex.get_unixtime(), '%I:%m%p, %B %d, %Y')
    md_lines = [
        '# Textbooks',
        '*From [Educational Publications Department]'
        + '(http://www.edupub.gov.lk/BooksDownload.php)*',
        '## Contents',
        f'Upload time: **{time_str}**',
    ]
    for lang_id, lang_entries in index_entries.items():

        dir_lang = os.path.join(REMOTE_DIR_DOCS, lang_id)
        md_lines.append(f'* [{lang_id}]({dir_lang})')
        for grade_id, grade_entries in lang_entries.items():

            dir_grade = os.path.join(dir_lang, grade_id)
            md_lines.append(f'  * [{grade_id}]({dir_grade})')
            for book_id, book_entries in grade_entries.items():

                dir_book = os.path.join(dir_grade, book_id)
                md_lines.append(f'    * [{book_id}]({dir_book})')
                for data in book_entries:
                    chapter_id = data['chapter_id']
                    file_chapter = os.path.join(dir_book, chapter_id)
                    md_lines.append(f'      * [{chapter_id}]({file_chapter})')

    md_file = '/tmp/lk_textbooks/docs/README.md'
    filex.write(md_file, '\n\n'.join(md_lines))
    log.info(f'Wrote summary to {md_file}')


if __name__ == '__main__':
    init()
    download()
    build_summary_md()
