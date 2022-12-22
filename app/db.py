import datetime

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, String, Date

from passlib.hash import sha256_crypt
from datetime import date


metadata = MetaData()


user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(32)),
    Column('surname', String(32)),
    Column('login', String(128), unique=True),
    Column('password', String(256)),
    Column('date_of_birth', Date),
    Column('permissions', ForeignKey('permissions.id', ondelete='SET NULL'), default=3),
)


permissions = Table(
    'permissions',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('perm_name', String(10)),
)


async def setup_db(app):
    db_url = app['config']['db_url']
    engine = create_async_engine(
        db_url,
        echo=True,
        future=True,
    )
    app['db'] = engine


async def create_admin(engine):
    async with engine.connect() as conn:
        await conn.execute(
            user.insert(), {
                'id': 1,
                'name': 'admin',
                'surname': 'admin',
                'login': 'admin',
                'password': sha256_crypt.using().hash('admin'),
                'date_of_birth': datetime.date(1970, 1, 1),
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
