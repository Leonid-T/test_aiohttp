from aiohttp import web
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy

from server.web.settings.conf import config
from server.web.routes import routes_list
from server.web.middlewares import error_middleware
from server.db.auth import DBAuthorizationPolicy
from server.db import opt


async def get_db():
    db_url = 'postgresql+asyncpg://postgres:admin@localhost:5432/test_db'
    engine = await opt.create_db_engine(db_url=db_url, echo=False)
    await opt.create_tables(engine)
    await opt.create_def_permissions(engine)
    await opt.create_admin(engine)
    return engine


async def get_app():
    app = web.Application()
    app.add_routes(routes_list)
    app.on_startup.append(on_start)
    app.on_shutdown.append(on_shutdown)
    app.middlewares.append(error_middleware)
    return app


async def on_start(app):
    app['db'] = await get_db()
    setup_session(app, EncryptedCookieStorage(bytes(config['cookie_key'], 'utf-8')))
    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(app['db']))


async def on_shutdown(app):
    engine = app['db']
    await opt.delete_tables(engine)
    await engine.dispose()
