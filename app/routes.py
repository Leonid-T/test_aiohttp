from aiohttp import web
from . import views


routes_list = [
    web.post('/login', views.handler_login),
    web.post('/logout', views.handler_logout),
    web.post('/user', views.create_user),
    web.get('/user', views.read_user),
    web.patch('/user', views.update_user),
    web.delete('/user', views.delete_user),
]
