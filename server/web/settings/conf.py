import pathlib
import logging


DEBUG = False

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

config = {
    'db_url': 'postgresql+asyncpg://postgres:admin@postgres:5432',
    'debug_db_url': 'postgresql+asyncpg://postgres:admin@localhost:5432/test_aiohttp',
    'log_path': 'server.log',
    'cookie_key': 'fa5s3nuzsfhzlgnfdgv86g1rdg7sd361',  # length must be 32 characters
    'docs_url': '/backend',
}

logging.basicConfig(level=logging.DEBUG, filename=BASE_DIR / config['log_path'], filemode='w')
