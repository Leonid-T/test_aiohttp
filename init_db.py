import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.settings import config
from app.db import metadata, create_def_permissions, create_admin


async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)


async def async_main():
    db_url = config['db_url']
    engine = create_async_engine(
        db_url,
        echo=True,
        future=True,
    )
    await create_tables(engine)
    await create_def_permissions(engine)
    await create_admin(engine)
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
