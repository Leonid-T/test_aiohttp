from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec

from srv.store.pg.accessor import setup_accessors
from srv.actions.managers import setup_model_managers
from srv.settings.config import CONFIG
from srv.web.routes import routes_list
from srv.web.middlewares import setup_middlewares


async def create_app():
    """
    Server initialization and configuration
    """
    app = web.Application()
    app['config'] = CONFIG
    app.add_routes(routes_list)
    setup_accessors(app)
    setup_model_managers(app)
    setup_middlewares(app)
    setup_aiohttp_apispec(app, swagger_path=app['config']['docs_url'])
    return app
