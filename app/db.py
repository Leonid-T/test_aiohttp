from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, Sequence, ForeignKey, Integer, String, Date

from passlib.hash import sha256_crypt
from datetime import date

from .settings import config


metadata = MetaData()
engine = create_async_engine(
    config['db_url'],
    echo=True,
    future=True,
)


user = Table(
    'user',
    metadata,
    Column('id', Integer, Sequence('some_id_seq', start=2), primary_key=True),
    Column('name', String(32)),
    Column('surname', String(32)),
    Column('login', String(128), unique=True, nullable=False),
    Column('password', String(256), nullable=False),
    Column('date_of_birth', Date),
    Column('permissions', ForeignKey('permissions.id', ondelete='SET NULL'), default=3),
)


permissions = Table(
    'permissions',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('perm_name', String(10), nullable=False),
)


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
