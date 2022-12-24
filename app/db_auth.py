from aiohttp_security.abc import AbstractAuthorizationPolicy

import sqlalchemy as sa
from passlib.hash import sha256_crypt

from . import db


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, engine):
        self.engine = engine

    async def authorized_userid(self, identity):
        async with self.engine.connect() as conn:
            ret = await conn.scalar(
                sa.select(db.user.c.login, db.user.c.password, db.permissions.c.perm_name)
                .where(
                    sa.and_(
                        db.user.c.permissions == db.permissions.c.id,
                        db.user.c.login == identity,
                        db.permissions.c.perm_name != 'block'
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
                sa.select(db.user.c.login, db.user.c.password, db.permissions.c.perm_name)
                .where(
                    sa.and_(
                        db.user.c.permissions == db.permissions.c.id,
                        db.user.c.login == identity,
                        db.permissions.c.perm_name != 'block'
                    )
                )
            )
        user = ret.fetchone()
        if user is not None:
            perm = user[2]
            if perm == permission:
                return True
        return False


async def check_credentials(login, password):
    async with db.engine.connect() as conn:
        ret = await conn.execute(
            sa.select(db.user.c.login, db.user.c.password, db.permissions.c.perm_name)
            .where(
                sa.and_(
                    db.user.c.permissions == db.permissions.c.id,
                    db.user.c.login == login,
                    db.permissions.c.perm_name != 'block'
                )
            )
        )
    user = ret.fetchone()
    if user is not None:
        hashed_password = user[1]
        return sha256_crypt.verify(password, hashed_password)
    return False
