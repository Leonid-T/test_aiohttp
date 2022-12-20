from aiohttp import web


from .routes import setup_routes
from .settings import config
from .db import pg_context


async def create_app():
    app = web.Application()
    app['config'] = config
    setup_routes(app)
    app.cleanup_ctx.append(pg_context)
    return app
