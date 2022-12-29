from aiohttp import web

from . import views


routes_list = [
    web.post('/login', views.login),
    web.post('/logout', views.logout),
    web.view('/user', views.UserView),
    web.view('/user/{slug}', views.OneUserView),
]
