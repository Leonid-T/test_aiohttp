import string
import random

from sqlalchemy.ext.asyncio import create_async_engine
from passlib.hash import sha256_crypt
from datetime import date, timedelta

from server.store.pg.models import user
from server.store.pg.opt import delete_tables, create_tables, create_def_permissions, create_admin


# change this url to connect to your test base
test_db_url = 'postgresql+asyncpg://postgres:admin@localhost:5432/test_db'


async def get_test_db_engine():
    """
    Create database engine with test configuration.
    """
    engine = create_async_engine(
        test_db_url,
        echo=False,
        future=True,
    )
    return engine


async def create_db_data():
    engine = await get_test_db_engine()
    try:
        async with engine.begin() as conn:
            await create_tables(conn)
            await create_def_permissions(conn)
            await create_admin(conn)
            await filing_db_tables(conn)
    finally:
        await engine.dispose()


async def delete_db_data():
    engine = await get_test_db_engine()
    try:
        async with engine.begin() as conn:
            await delete_tables(conn)
    finally:
        await engine.dispose()


async def filing_db_tables(conn):
    """
    Filling the user table with test data.
    """
    await conn.execute(
        user.insert(), [
            {
                'name': random_text(5),
                'surname': random_text(5),
                'login': random_text(4) + str(i),
                'password': sha256_crypt.using().hash(random_text(5)),
                'date_of_birth': random_date(),
            }
            for i in range(10)
        ]
    )


def random_text(n):
    return ''.join([random.choice(string.ascii_letters) for _ in range(n)])


def random_date():
    start_date = date(1920, 1, 1)
    end_date = date(2020, 1, 1)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)
