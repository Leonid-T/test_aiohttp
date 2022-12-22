from aiohttp import web
from aiohttp_security import remember, forget, check_authorized

from .db_auth import check_credentials


async def handler_login(request):
    invalid_response = web.json_response({'error': 'Invalid username/password combination'}, status=400)
    try:
        data = await request.json()
    except Exception:
        return invalid_response
    login = data.get('login')
    password = data.get('password')
    engine = request.app['db']

    if not (isinstance(login, str) and isinstance(password, str)):
        return invalid_response

    if await check_credentials(engine, login, password):
        response = web.json_response(status=200)
        await remember(request, response, login)
        return response

    return invalid_response


async def handler_logout(request):
    await check_authorized(request)
    response = web.json_response(status=200)
    await forget(request, response)
    return response


async def create_user(request):
    data = {'status': 'success'}
    return web.json_response(data)


async def read_user(request):
    data = {'status': 'success'}
    return web.json_response(data)


async def update_user(request):
    data = {'status': 'success'}
    return web.json_response(data)


async def delete_user(request):
    data = {'status': 'success'}
    return web.json_response(data)
