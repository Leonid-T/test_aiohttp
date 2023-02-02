import random
import sqlalchemy as sa

from passlib.hash import sha256_crypt

from srv.store.pg.models import user, permissions
from srv.web.validations import UserModel


async def insert_user(conn, login, password, perm='read'):
    perm_id = await conn.scalar(
        sa.select(permissions.c.id).where(permissions.c.perm_name == perm)
    )
    await conn.execute(user.insert(), {
        'login': login,
        'password': sha256_crypt.using().hash(password),
        'permissions': perm_id
    })


async def validate_user(user_data):
    UserModel(**user_data)


async def random_user_id(conn):
    ret = await conn.execute(
        sa.select(user.c.id).where(user.c.login != 'admin')
    )
    list_of_id = [row[0] for row in ret]
    return random.choice(list_of_id)


async def random_user_login(conn):
    ret = await conn.execute(
        sa.select(user.c.login).where(user.c.login != 'admin')
    )
    list_of_login = [row[0] for row in ret]
    return random.choice(list_of_login)
