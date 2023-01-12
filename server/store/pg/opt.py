from sqlalchemy.ext.asyncio import create_async_engine

from passlib.hash import sha256_crypt
from datetime import date

from server.web.settings.conf import config, DEBUG
from .models import metadata, user, permissions


async def create_db_engine(db_url=config['db_url'], echo=True):
    if DEBUG:
        db_url = config['test_db_url']
        echo = False
    engine = create_async_engine(
        db_url,
        echo=echo,
        future=True,
    )
    return engine


async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)


async def delete_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


async def create_admin(engine):
    async with engine.connect() as conn:
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
        await conn.commit()


async def create_def_permissions(engine):
    async with engine.connect() as conn:
        await conn.execute(
            permissions.insert(), [
                {'id': 1, 'perm_name': 'block'},
                {'id': 2, 'perm_name': 'admin'},
                {'id': 3, 'perm_name': 'read'},
            ]
        )
        await conn.commit()
