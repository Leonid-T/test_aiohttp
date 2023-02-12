import string
import random
import sqlalchemy as sa

from passlib.hash import sha256_crypt
from datetime import date, timedelta

from srv.store.pg.models import user, permissions
from srv.web.schemas import UserSchema, UserCreateSchema


async def insert_user(conn, data):
    """
    Safe insert user into database
    """
    user_data = UserCreateSchema().load(data)
    perm_name = user_data.get('permissions', 'read')
    perm_id = await conn.scalar(
        sa.select(permissions.c.id).where(permissions.c.perm_name == perm_name)
    )
    user_data['permissions'] = perm_id
    user_data['password'] = sha256_crypt.using().hash(user_data['password'])

    user_login = await conn.scalar(
        user.insert().values(user_data).returning(user.c.login)
    )
    assert user_login == user_data['login']


async def insert_random_user(conn):
    """
    Safe insert random user into database
    """
    user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(),
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }
    await insert_user(conn, user_data)
    return await get_user_by_login(conn, user_data['login'])


async def filing_db_table_user(conn, size=5):
    """
    Filling the user table with test data
    """
    for i in range(size):
        user_data = {
            'name': random_text(),
            'surname': random_text(),
            'login': random_text(4) + str(i),  # ensure unique login field
            'password': random_text(),
            'date_of_birth': random_date(),
            'permissions': random_permissions(),
        }
        await insert_user(conn, user_data)


async def validate_user_initial_data(initial_data, returned_data):
    """
    Checking that the initial user data is equal to the returned user data
    """
    for key in initial_data:
        if key == 'password':
            assert sha256_crypt.verify(initial_data[key], returned_data[key]) is True
        else:
            assert initial_data[key] == returned_data[key]


async def validate_user_db_data(conn, returned_data):
    """
    Checking that the returned user data is equal to the user data in the database
    """
    db_user_data = await get_user_by_login(conn, returned_data['login'])
    assert returned_data == db_user_data


async def get_user_by_login(conn, login):
    """
    Get user data in the database by login
    """
    ret = await conn.execute(
        sa.select(
            user.c.id,
            user.c.name,
            user.c.surname,
            user.c.login,
            user.c.password,
            user.c.date_of_birth,
            permissions.c.perm_name.label('permissions'),
        ).where(user.c.permissions == permissions.c.id, user.c.login == login)
    )
    row = ret.fetchone()
    assert row is not None
    return UserSchema().dump(row)


async def check_deletion(conn, login):
    """
    checking if user is deleted using login
    """
    user_id = await conn.scalar(
        sa.select(user.c.id).where(user.c.login == login)
    )
    assert user_id is None


def random_text(size=5):
    """
    Random ascii letters string
    """
    return ''.join([random.choice(string.ascii_letters) for _ in range(size)])


def random_date():
    """
    String iso format from random date
    """
    start_date = date(1920, 1, 1)
    end_date = date(2020, 1, 1)
    days_between_dates = (end_date - start_date).days
    random_number_of_days = random.randrange(days_between_dates)
    return (start_date + timedelta(days=random_number_of_days)).isoformat()


def random_permissions():
    """
    Random user permissions
    """
    return random.choice(('admin', 'read', 'block'))
