from sqlalchemy.ext.asyncio import create_async_engine


async def pg_context(app):
    db_url = app['config']['db_url']
    engine = create_async_engine(
        db_url,
        echo=True,
        future=True,
    )
    app['db'] = engine

    yield

    await app['db'].dispose()
