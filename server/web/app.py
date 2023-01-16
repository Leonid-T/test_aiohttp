from aiohttp import web

from aiohttp_swagger import setup_swagger

from server.store.pg.accessor import setup_accessors

from .settings.conf import config
from .routes import routes_list
from .middlewares import setup_middlewares


async def create_app():
    """
    Server initialization and configuration.
    """
    app = web.Application()
    app['config'] = config
    app.add_routes(routes_list)
    setup_accessors(app)
    setup_middlewares(app)
    setup_swagger(app, swagger_url=app['config']['docs_url'])
    return app
