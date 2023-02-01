from aiohttp import web
from aiohttp_pydantic import oas

from server.store.pg.accessor import setup_accessors
from server.store.pg.api import setup_models

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
    setup_models(app)
    setup_middlewares(app)
    oas.setup(app, url_prefix=app['config']['docs_url'])
    return app
