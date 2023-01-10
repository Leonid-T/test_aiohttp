from aiohttp import web
from sqlalchemy.exc import IntegrityError

from json.decoder import JSONDecodeError
from jsonschema.exceptions import ValidationError


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
    except (JSONDecodeError, ValidationError, ValueError, IntegrityError):
        return web.json_response({'error': 'Invalid data'}, status=400)
    return response
