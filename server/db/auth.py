from aiohttp_security.abc import AbstractAuthorizationPolicy

import sqlalchemy as sa
from passlib.hash import sha256_crypt

from . import models


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, engine):
        self.engine = engine

    async def authorized_userid(self, identity):
        async with self.engine.connect() as conn:
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
        else:
            return None

    async def permits(self, identity, permission, context=None):
        async with self.engine.connect() as conn:
            ret = await conn.execute(
                sa.select(models.user.c.login, models.user.c.password, models.permissions.c.perm_name)
                .where(
                    sa.and_(
                        models.user.c.permissions == db.permissions.c.id,
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
        return False


async def check_credentials(engine, login, password):
    async with engine.connect() as conn:
        ret = await conn.execute(
            sa.select(models.user.c.login, models.user.c.password, models.permissions.c.perm_name)
            .where(
                sa.and_(
                    models.user.c.permissions == models.permissions.c.id,
                    models.user.c.login == login,
                    models.permissions.c.perm_name != 'block'
                )
            )
        )
    user = ret.fetchone()
    if user is not None:
        hashed_password = user[1]
        return sha256_crypt.verify(password, hashed_password)
    return False
