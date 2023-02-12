import os
import sys
import pathlib
import logging
from sqlalchemy.engine import URL


BASE_DIR = pathlib.Path(__file__).parent.parent.parent


# default application config
CONFIG = {
    'db_url': URL(
        drivername='postgresql+asyncpg',
        database=os.environ.get('POSTGRES_DB', 'test_db'),
        username=os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('POSTGRES_PASSWORD', 'admin'),
        host=os.environ.get('SQL_HOST', 'localhost'),
        port=os.environ.get('SQL_PORT', '5432'),
        query={},
    ),
    'log_path': 'srv.log',
    'cookie_key': 'fa5s3nuzsfhzlgnfdgv86g1rdg7sd361',  # length must be 32 characters
    'docs_url': '/backend',
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / CONFIG['log_path']),
        logging.StreamHandler(sys.stdout)
    ],
)
