from aiohttp import web
from aiohttp_security import remember, forget, check_authorized, check_permission
from aiohttp_swagger import swagger_path

from json.decoder import JSONDecodeError

from .db_auth import check_credentials
from .db_api import User


@swagger_path('app/swagger/login.yaml')
async def login(request):
    invalid_response = web.json_response(
        {'error': 'Invalid username/password combination or this user is blocked'}, status=400
    )
    try:
        data = await request.json()
    except JSONDecodeError:
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


@swagger_path('app/swagger/logout.yaml')
async def logout(request):
    await check_authorized(request)
    response = web.json_response(status=200)
    await forget(request, response)
    return response


@swagger_path('app/swagger/create_user.yaml')
async def create_user(request):
    await check_authorized(request)
    await check_permission(request, 'admin')
    invalid_response = web.json_response({'error': 'Invalid data'}, status=400)
    try:
        user_data = await request.json()
    except JSONDecodeError:
        return invalid_response

    engine = request.app['db']
    user = User(engine)
    error = await user.create(user_data)
    if error:
        return invalid_response

    return web.json_response(status=200)


@swagger_path('app/swagger/read_user_all.yaml')
async def read_user_all(request):
    await check_authorized(request)
    engine = request.app['db']
    user = User(engine)
    users_list = await user.read_all()
    return web.json_response(users_list, status=200)


@swagger_path('app/swagger/read_user.yaml')
async def read_user(request):
    await check_authorized(request)
    slug = request.match_info.get('slug')
    engine = request.app['db']
    user = User(engine)
    user_data = await user.read(slug)
    return web.json_response(user_data, status=200)


@swagger_path('app/swagger/update_user.yaml')
async def update_user(request):
    await check_authorized(request)
    await check_permission(request, 'admin')
    invalid_response = web.json_response({'error': 'Invalid data'}, status=400)
    try:
        user_data = await request.json()
    except JSONDecodeError:
        return invalid_response

    slug = request.match_info.get('slug')
    engine = request.app['db']
    user = User(engine)
    error = await user.update(slug, user_data)
    if error:
        return invalid_response

    return web.json_response(status=200)


@swagger_path('app/swagger/delete_user.yaml')
async def delete_user(request):
    await check_authorized(request)
    await check_permission(request, 'admin')
    slug = request.match_info.get('slug')
    engine = request.app['db']
    user = User(engine)
    await user.delete(slug)
    return web.json_response(status=200)
