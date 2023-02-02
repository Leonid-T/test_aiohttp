import pytest_asyncio

from aiohttp.web import HTTPForbidden

from srv.settings.app import create_app
from tests.init_app import get_test_db_engine


class Client:
    def __init__(self, _client):
        self.client = _client

    async def __aenter__(self):
        self.engine = await get_test_db_engine()
        self.conn = await self.engine.connect()
        self.client.conn = self.conn
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.rollback()
        await self.conn.close()
        await self.engine.dispose()


@pytest_asyncio.fixture
async def client(aiohttp_client, mocker):
    """
    Default unauthorized client fixture.
    """
    app = await create_app()
    http_client = await aiohttp_client(app)
    async with Client(http_client) as CLIENT:
        mocker.patch('srv.store.pg.accessor.PGConnect.__aenter__', return_value=CLIENT.conn)
        mocker.patch('srv.store.pg.accessor.PGConnect.__aexit__', return_value=None)
        yield CLIENT
    await http_client.close()


@pytest_asyncio.fixture
async def client_admin(aiohttp_client, mocker):
    """
    Client fixture with admin permissions.
    """
    app = await create_app()
    http_client = await aiohttp_client(app)
    async with Client(http_client) as CLIENT:
        mocker.patch('srv.store.pg.accessor.PGConnect.__aenter__', return_value=CLIENT.conn)
        mocker.patch('srv.store.pg.accessor.PGConnect.__aexit__', return_value=None)
        mocker.patch('srv.web.views.check_authorized', return_value=None)
        mocker.patch('srv.web.views.check_permission', return_value=None)
        yield CLIENT
    await http_client.close()


@pytest_asyncio.fixture
async def client_read(aiohttp_client, mocker):
    """
    Client fixture with read permissions.
    """
    app = await create_app()
    http_client = await aiohttp_client(app)
    async with Client(http_client) as CLIENT:
        mocker.patch('srv.store.pg.accessor.PGConnect.__aenter__', return_value=CLIENT.conn)
        mocker.patch('srv.store.pg.accessor.PGConnect.__aexit__', return_value=None)
        mocker.patch('srv.web.views.check_authorized', return_value=None)
        mocker.patch('srv.web.views.check_permission', side_effect=HTTPForbidden)
        yield CLIENT
    await http_client.close()
