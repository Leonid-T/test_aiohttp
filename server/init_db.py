import asyncio

from server.store.pg.opt import create_db_engine, create_tables, create_def_permissions, create_admin


async def async_main():
    """
    Database initialization with url = config['db_url']:
    creating tables and default data.
    """
    engine = await create_db_engine()
    try:
        async with engine.begin() as conn:
            await create_tables(conn)
            await create_def_permissions(conn)
            await create_admin(conn)
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
