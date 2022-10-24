import os
import logging

from ..settings import settings

LOGGING_FILE_PATH: str = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ), '..', settings.LOGGING_FILENAME
)

if not os.path.exists(LOGGING_FILE_PATH):
    open(LOGGING_FILE_PATH, 'a').close()

if (
    os.path.getsize(LOGGING_FILE_PATH) // (1024 * 1024)
    >= settings.CLEAR_LOGGING_FILE_SIZE_LIMIT
):
    open(LOGGING_FILE_PATH, 'w').close()  # erase file content

logging.basicConfig(
    format='%(asctime)s, %(msecs)d %(name)s %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
    level=settings.LOGGING_LEVEL,
    handlers=[
        logging.FileHandler(LOGGING_FILE_PATH, mode='a+'),
        logging.StreamHandler()
    ]
)

FISHER_BOT_LOGGER = logging.getLogger('FISHER_BOT')
COMPONENTS_LOGGER = logging.getLogger('COMPONENETS_LOGGER')
