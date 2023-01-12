import asyncio

from server.store.pg.opt import create_db_engine, create_tables, create_def_permissions, create_admin


async def async_main():
    engine = await create_db_engine()
    try:
        await create_tables(engine)
        await create_def_permissions(engine)
        await create_admin(engine)
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
