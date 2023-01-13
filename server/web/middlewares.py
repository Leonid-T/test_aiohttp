from aiohttp import web
from sqlalchemy.exc import IntegrityError, DBAPIError

from json.decoder import JSONDecodeError
from jsonschema.exceptions import ValidationError


def setup_middlewares(app):
    app.middlewares.append(error_middleware)
    app.middlewares.append(db_connect_middleware)


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
    except (JSONDecodeError, ValidationError, ValueError, IntegrityError, DBAPIError):
        return web.json_response({'error': 'Invalid data'}, status=400)
    return response


@web.middleware
async def db_connect_middleware(request, handler):
    db = request.app.db
    async with db.begin() as conn:
        request.app['conn'] = conn
        response = await handler(request)
    return response
