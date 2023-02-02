from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy

from .options import create_db_engine
from srv.actions.authorization import DBAuthorizationPolicy


def setup_accessors(app):
    db_accessor = PostgresAccessor()
    db_accessor.setup(app)


class PostgresAccessor:
    """
    Database connections, get transaction management.
    """

    def __init__(self):
        self.engine = None

    def setup(self, app):
        app.on_startup.append(self._on_connect)
        app.on_shutdown.append(self._on_disconnect)

    async def _on_connect(self, app):
        self.engine = await create_db_engine()
        app.db = self

        cookie_key = bytes(app['config']['cookie_key'], 'utf-8')
        setup_session(app, EncryptedCookieStorage(cookie_key))
        setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(self))

    async def _on_disconnect(self, app):
        if self.engine is not None:
            await self.engine.dispose()

    def connect(self):
        """
        Database connection without commit.
        """
        if self.engine is None:
            return
        _connect = PGConnect(self.engine)
        return _connect

    def begin(self):
        """
        Database connection with commit.
        """
        _connect = PGConnect(self.engine, True)
        return _connect


class PGConnect:
    """
    Transaction management.
    """

    def __init__(self, engine, _is_transaction=False):
        self.engine = engine
        self._is_transaction = _is_transaction

    async def __aenter__(self):
        self.conn = await self.engine.connect()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._is_transaction and not exc_type:
            await self.conn.commit()
        await self.conn.close()
