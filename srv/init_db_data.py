import asyncio

from srv.store.pg.options import create_db_engine, check_default_data


async def async_main():
    """
    Creating default data if it isn't exist
    """
    engine = await create_db_engine()
    try:
        async with engine.begin() as conn:
            await check_default_data(conn)
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())