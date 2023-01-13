from sqlalchemy.ext.asyncio import create_async_engine

from passlib.hash import sha256_crypt
from datetime import date

from server.web.settings.conf import config
from .models import metadata, user, permissions


async def create_db_engine():
    engine = create_async_engine(
        config['db_url'],
        echo=True,
        future=True,
    )
    return engine


async def create_tables(conn):
    await conn.run_sync(metadata.drop_all)
    await conn.run_sync(metadata.create_all)


async def delete_tables(conn):
    await conn.run_sync(metadata.drop_all)


async def create_admin(conn):
    await conn.execute(
        user.insert(), {
            'id': 1,
            'name': 'admin',
            'surname': 'admin',
            'login': 'admin',
            'password': sha256_crypt.using().hash('admin'),
            'date_of_birth': date.fromisoformat('1970-01-01'),
            'permissions': 2,
        }
    )


async def create_def_permissions(conn):
    await conn.execute(
        permissions.insert(), [
            {'id': 1, 'perm_name': 'block'},
            {'id': 2, 'perm_name': 'admin'},
            {'id': 3, 'perm_name': 'read'},
        ]
    )
