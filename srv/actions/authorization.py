from aiohttp_security.abc import AbstractAuthorizationPolicy

import sqlalchemy as sa
from passlib.hash import sha256_crypt

from srv.store.pg import models


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    """
    Authorization policy for aiohttp_security
    """

    def __init__(self, db):
        self.db = db

    async def authorized_userid(self, identity):
        async with self.db.connect() as conn:
            ret = await conn.scalar(
                sa.select(models.user.c.login, models.user.c.password, models.permissions.c.perm_name)
                .where(
                    sa.and_(
                        models.user.c.permissions == models.permissions.c.id,
                        models.user.c.login == identity,
                        models.permissions.c.perm_name != 'block'
                    )
                )
            )
            if ret:
                return identity

    async def permits(self, identity, permission, context=None):
        async with self.db.connect() as conn:
            ret = await conn.execute(
                sa.select(models.user.c.login, models.user.c.password, models.permissions.c.perm_name)
                .where(
                    sa.and_(
                        models.user.c.permissions == models.permissions.c.id,
                        models.user.c.login == identity,
                        models.permissions.c.perm_name != 'block'
                    )
                )
            )
            user = ret.fetchone()
            if user is not None:
                perm = user[2]
                if perm == permission:
                    return True


async def check_credentials(conn, data):
    login = data['login']
    password = data['password']

    hashed_password = await conn.scalar(
            sa.select(models.user.c.password)
            .where(
                sa.and_(
                    models.user.c.permissions == models.permissions.c.id,
                    models.user.c.login == login,
                    models.permissions.c.perm_name != 'block'
                )
            )
        )

    if hashed_password is not None:
        return sha256_crypt.verify(password, hashed_password)
