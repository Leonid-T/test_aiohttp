from aiohttp import web

from . import views


routes_list = [
    web.view('/login', views.LoginView),
    web.view('/logout', views.LogoutView),
    web.view('/user', views.UserView),
    web.view('/user/{slug}', views.OneUserView),
]
