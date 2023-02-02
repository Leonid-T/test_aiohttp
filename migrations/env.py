from logging.config import fileConfig

import asyncio

from alembic import context

from srv.store.pg.models import metadata
from srv.store.pg.options import create_db_engine


config = context.config
fileConfig(config.config_file_name)
target_metadata = metadata


def do_run_migrations(connection):
    context.configure(
        connection=connection, target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = await create_db_engine()

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


asyncio.run(run_migrations_online())
