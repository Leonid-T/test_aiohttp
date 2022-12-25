import asyncio

from app.db import engine, create_tables, create_def_permissions, create_admin


async def async_main():
    try:
        await create_tables(engine)
        await create_def_permissions(engine)
        await create_admin(engine)
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(async_main())
