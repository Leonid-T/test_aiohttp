from aiohttp import web
from . import views


routes_list = [
    web.post('/login', views.login),
    web.post('/logout', views.logout),
    web.post('/user', views.create_user),
    web.get('/user', views.read_user_all),
    web.get('/user/{slug}', views.read_user),
    web.patch('/user/{slug}', views.update_user),
    web.delete('/user/{slug}', views.delete_user),
]
