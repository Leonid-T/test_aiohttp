from aiohttp import web
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy
from aiohttp_swagger import setup_swagger

from .db import engine
from .db_auth import DBAuthorizationPolicy
from .routes import routes_list
from .settings import config


async def create_app():
    app = web.Application()
    app['config'] = config
    app.add_routes(routes_list)
    app.on_startup.append(on_start)
    app.on_shutdown.append(on_shutdown)
    setup_swagger(app, swagger_url='/backend')
    return app


async def on_start(app):
    app['db'] = engine
    setup_session(app, EncryptedCookieStorage(bytes(app['config']['cookie_key'], 'utf-8')))
    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(app['db']))


async def on_shutdown(app):
    await app['db'].dispose()
