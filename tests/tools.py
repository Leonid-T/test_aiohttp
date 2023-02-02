import random
import sqlalchemy as sa

from passlib.hash import sha256_crypt
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional
from datetime import date

from srv.store.pg.models import user, permissions


async def insert_user(conn, login, password, perm='read'):
    perm_id = await conn.scalar(
        sa.select(permissions.c.id).where(permissions.c.perm_name == perm)
    )
    await conn.execute(user.insert(), {
        'login': login,
        'password': sha256_crypt.using().hash(password),
        'permissions': perm_id
    })


class UserOutModel(BaseModel):
    id: int
    name: Optional[Annotated[str, Field(max_length=32)]]
    surname: Optional[Annotated[str, Field(max_length=32)]]
    login: Annotated[str, Field(max_length=128)]
    password: str
    date_of_birth: Optional[date]
    permissions: Literal['admin', 'read', 'block']


async def validate_user(user_data):
    UserOutModel(**user_data)


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
