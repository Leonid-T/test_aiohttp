from sqlalchemy.ext.asyncio import create_async_engine

from passlib.hash import sha256_crypt
from datetime import date

from srv.settings.config import CONFIG
from .models import user, permissions


async def create_db_engine():
    """
    Create database engine with default configuration.
    """
    engine = create_async_engine(
        CONFIG['db_url'],
        echo=True,
        future=True,
    )
    return engine


async def check_default_data(conn):
    """
    Create default admin and permissions if they are not exist.
    """
    admin = await conn.scalar(
        user.select().where(
            user.c.login == 'admin',
        )
    )
    if not admin:
        await create_def_permissions(conn)
        await create_admin(conn)


async def create_admin(conn):
    """
    Create default admin user.
    """
    await conn.execute(
        user.insert(), {
            'name': 'admin',
            'surname': 'admin',
            'login': 'admin',
            'password': sha256_crypt.using().hash('admin'),
            'date_of_birth': date.fromisoformat('1970-01-01'),
            'permissions': 2,
        }
    )


async def create_def_permissions(conn):
    """
    Create default permissions.
    """
    await conn.execute(
        permissions.insert(), [
            {'id': 1, 'perm_name': 'block'},
            {'id': 2, 'perm_name': 'admin'},
            {'id': 3, 'perm_name': 'read'},
        ]
    )
