import pathlib
import pytest
import pytest_asyncio

from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine

from srv.store.pg.options import create_def_permissions, create_admin


BASE_DIR = pathlib.Path(__file__).parent.parent

# change this url to connect to your test base
test_db_url = 'postgresql+asyncpg://postgres:admin@localhost:5432/test_db'


@pytest.fixture(scope='session', autouse=True)
def alembic_engine():
    engine = create_async_engine(
        test_db_url,
        echo=False,
        future=True,
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope='session', autouse=True)
def alembic_config():
    """
    Override this fixture to configure the exact alembic context setup required
    """
    alembic_cfg = Config(str(BASE_DIR / 'alembic.ini'))
    alembic_cfg.set_main_option('script_location', str(BASE_DIR / 'migrations'))
    alembic_cfg.set_section_option("logger_alembic", "level", "ERROR")
    return alembic_cfg


@pytest.fixture(scope='function', autouse=True)
def alembic_upgrade_downgrade(alembic_runner):
    """
    Upgrade and downgrade database with alembic
    """
    alembic_runner.migrate_down_to('base')
    alembic_runner.migrate_up_to('heads')
    yield
    alembic_runner.migrate_down_to('base')


@pytest_asyncio.fixture(scope='function', autouse=True)
async def create_def_data(alembic_engine):
    """
    Create default admin and permissions
    """
    try:
        async with alembic_engine.begin() as conn:
            await create_def_permissions(conn)
            await create_admin(conn)
    finally:
        await alembic_engine.dispose()
