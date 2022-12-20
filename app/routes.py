from aiohttp import web
from . import views


def setup_routes(app):
    app.add_routes([
        web.get('/create_user', views.create_user),
        web.get('/read_user', views.read_user),
        web.get('/update_user', views.update_user),
        web.get('/delete_user', views.delete_user),
    ])
