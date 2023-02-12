import pytest_asyncio

from aiohttp.web import HTTPForbidden

from srv.settings.app import create_app
from tests.fixtures import alembic_engine, alembic_config, alembic_upgrade_downgrade, create_def_data


class Client:
    def __init__(self, _client, _engine):
        self.client = _client
        self.engine = _engine

    async def __aenter__(self):
        self.conn = await self.engine.connect()
        self.client.conn = self.conn
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.rollback()
        await self.conn.close()


@pytest_asyncio.fixture(scope='function', autouse=True)
async def client(aiohttp_client, mocker, alembic_engine):
    """
    Default unauthorized client fixture
    """
    app = await create_app()
    http_client = await aiohttp_client(app)
    async with Client(http_client, alembic_engine) as CLIENT:
        mocker.patch('srv.store.pg.accessor.PGConnect.__aenter__', return_value=CLIENT.conn)
        mocker.patch('srv.store.pg.accessor.PGConnect.__aexit__', return_value=None)
        yield CLIENT
    await http_client.close()


@pytest_asyncio.fixture(scope='function')
async def auth_admin(mocker):
    """
    Authorization with admin permissions
    """
    mocker.patch('srv.web.views.check_authorized', return_value=None)
    mocker.patch('srv.web.views.check_permission', return_value=None)


@pytest_asyncio.fixture(scope='function')
async def auth_read(mocker):
    """
    Authorization with read permissions
    """
    mocker.patch('srv.web.views.check_authorized', return_value=None)
    mocker.patch('srv.web.views.check_permission', side_effect=HTTPForbidden)
