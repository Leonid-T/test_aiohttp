from aiohttp import web
from . import handlers


routes_list = [
    web.post('/login', handlers.login),
    web.post('/logout', handlers.logout),
    web.post('/user', handlers.create_user),
    web.get('/user', handlers.read_user_all),
    web.get('/user/{slug}', handlers.read_user),
    web.patch('/user/{slug}', handlers.update_user),
    web.delete('/user/{slug}', handlers.delete_user),
]
