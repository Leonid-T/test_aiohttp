from aiohttp import web
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy

from app.settings import config
from app.routes import routes_list
from app.db_auth import DBAuthorizationPolicy
from app import db


async def get_db():
    db_url = config['db_test_url']
    engine = await db.create_db_engine(db_url=db_url, echo=False)
    await db.create_tables(engine)
    await db.create_def_permissions(engine)
    await db.create_admin(engine)
    return engine


async def get_app():
    app = web.Application()
    app.add_routes(routes_list)
    app.on_startup.append(on_start)
    app.on_shutdown.append(on_shutdown)
    return app


async def on_start(app):
    app['db'] = await get_db()
    setup_session(app, EncryptedCookieStorage(bytes(config['cookie_key'], 'utf-8')))
    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(app['db']))


async def on_shutdown(app):
    engine = app['db']
    await db.delete_tables(engine)
    await engine.dispose()
