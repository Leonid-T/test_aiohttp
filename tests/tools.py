import random
import sqlalchemy as sa

from jsonschema import validate
from passlib.hash import sha256_crypt

from server.store.pg.models import user, permissions


async def insert_user(conn, login, password, perm='read'):
    perm_id = await conn.scalar(
        sa.select(permissions.c.id).where(permissions.c.perm_name == perm)
    )
    await conn.execute(user.insert(), {
        'login': login,
        'password': sha256_crypt.using().hash(password),
        'permissions': perm_id
    })


async def json_validate_user(json_data):
    schema = {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'name': {'type': 'string'},
            'surname': {'type': 'string'},
            'login': {'type': 'string'},
            'password': {'type': 'string'},
            'date_of_birth': {'type': 'string'},
            'permissions': {'type': 'string'},
        },
        'required': ['id', 'login', 'password', 'permissions'],
        'additionalProperties': False,
    }
    validate(instance=json_data, schema=schema)


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
