from aiohttp import web
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy
from aiohttp_swagger import setup_swagger

from db.opt import create_db_engine
from db.auth import DBAuthorizationPolicy
from web.settings.settings import config

from .routes import routes_list


async def create_app():
    app = web.Application()
    app['config'] = config
    app.add_routes(routes_list)
    app.on_startup.append(on_start)
    app.on_shutdown.append(on_shutdown)
    setup_swagger(app, swagger_url=app['config']['docs_url'])
    return app


async def on_start(app):
    app['db'] = await create_db_engine()
    setup_session(app, EncryptedCookieStorage(bytes(app['config']['cookie_key'], 'utf-8')))
    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(app['db']))


async def on_shutdown(app):
    await app['db'].dispose()
