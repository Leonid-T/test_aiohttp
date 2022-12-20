from aiohttp import web


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
