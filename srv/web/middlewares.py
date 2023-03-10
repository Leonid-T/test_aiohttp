from aiohttp import web
from aiohttp_apispec import validation_middleware
from sqlalchemy.exc import IntegrityError, DBAPIError


def setup_middlewares(app):
    app.middlewares.append(validation_middleware)
    app.middlewares.append(error_middleware)
    app.middlewares.append(db_connect_middleware)


@web.middleware
async def error_middleware(request, handler):
    """
    Middleware for errors related to incorrect data entry
    """
    try:
        response = await handler(request)
    except (IntegrityError, DBAPIError):
        return web.json_response({'error': 'Invalid data'}, status=400)
    return response


@web.middleware
async def db_connect_middleware(request, handler):
    """
    Creating a database connection
    """
    db = request.app.db
    async with db.begin() as conn:
        request.app['conn'] = conn
        response = await handler(request)
    return response
