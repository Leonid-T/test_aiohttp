from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy

from .opt import create_db_engine
from .auth import DBAuthorizationPolicy


class PostgresAccessor:
    def __init__(self):
        self.engine = None

    def setup(self, app):
        app.on_startup.append(self._on_connect)
        app.on_shutdown.append(self._on_disconnect)

    async def _on_connect(self, app):
        self.engine = await create_db_engine()
        app['db'] = self.engine
        setup_session(app, EncryptedCookieStorage(bytes(app['config']['cookie_key'], 'utf-8')))
        setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(self.engine))

    async def _on_disconnect(self, app):
        if self.engine is not None:
            await self.engine.dispose()


def setup_accessors(app):
    db_accessor = PostgresAccessor()
    db_accessor.setup(app)
