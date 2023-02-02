import os
import pathlib
import logging


BASE_DIR = pathlib.Path(__file__).parent.parent.parent

# postgres config from environ
PG_CONFIG = {
    'name': os.environ.get("POSTGRES_DB"),
    'user': os.environ.get("POSTGRES_USER"),
    'password': os.environ.get("POSTGRES_PASSWORD"),
}

# default application config
CONFIG = {
    'db_url': f'postgresql+asyncpg://{PG_CONFIG["user"]}:{PG_CONFIG["password"]}@postgres:5432/{PG_CONFIG["name"]}',
    'log_path': 'srv.log',
    'cookie_key': 'fa5s3nuzsfhzlgnfdgv86g1rdg7sd361',  # length must be 32 characters
    'docs_url': '/backend',
}

logging.basicConfig(level=logging.DEBUG, filename=BASE_DIR / CONFIG['log_path'], filemode='w')
