import asyncio

from app.db import metadata, engine, create_def_permissions, create_admin


async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)


async def async_main():
    try:
        await create_tables(engine)
        await create_def_permissions(engine)
        await create_admin(engine)
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
