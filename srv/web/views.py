from aiohttp import web
from aiohttp_security import remember, forget, check_authorized, check_permission
from aiohttp_apispec import docs, request_schema, response_schema

from srv.actions.authorization import check_credentials

from .schemas import LoginSchema, UserSchema, UserCreateSchema


@docs(
    tags=['Authorization'],
    summary='User session authorization',
    description='This can only be done by an unblocked users',
    responses={
        200: {'description': 'Successful operation'},
        400: {'description': 'Invalid username/password combination or this user is blocked'},
        422: {"description": "Validation error"},
    },
)
@request_schema(LoginSchema)
async def login(request):
    """
    User session authorization
    """
    conn = request.app['conn']
    data = request['data']
    if not await check_credentials(conn, data):
        return web.json_response(
            {'error': 'Invalid username/password combination or this user is blocked'}, status=400
        )

    response = web.json_response(status=200)
    await remember(request, response, data['login'])
    return response


@docs(
    tags=['Authorization'],
    summary='Session terminate',
    description='This can only be done if you are authorized',
    responses={
        200: {'description': 'Successful operation'},
        401: {'description': "You aren't authorized"},
    },
)
async def logout(request):
    """
    Session terminate
    """
    await check_authorized(request)

    response = web.json_response(status=200)
    await forget(request, response)
    return response


class UserView(web.View):
    @docs(
        tags=['User'],
        summary='Create new user',
        description='This can only be done by authorized users with admin permissions',
        responses={
            201: {'description': 'Successful operation', 'schema': UserSchema},
            400: {'description': 'Invalid data, insert error'},
            401: {'description': "You aren't authorized"},
            403: {'description': "You haven't permissions"},
            422: {"description": "Validation error"},
        },
    )
    @request_schema(UserCreateSchema)
    @response_schema(UserSchema, 201)
    async def post(self):
        """
        Create new user
        """
        await check_permission(self.request, 'admin')

        conn = self.request.app['conn']
        user = self.request.app['model']['user']

        user_data = self.request['data']
        created_user = await user.create(conn, user_data)
        if not created_user:
            return web.json_response({'error': 'Insert error'}, status=400)

        return web.json_response(UserSchema().dump(created_user), status=201)

    @docs(
        tags=['User'],
        summary='Get list of users',
        description='This can only be done by authorized users',
        responses={
            200: {'description': 'Successful operation, return list of users'},
            401: {'description': "You aren't authorized"},
        },
    )
    async def get(self):
        """
        Get list of users
        """
        await check_authorized(self.request)

        conn = self.request.app['conn']
        user = self.request.app['model']['user']

        users_list = await user.read_all(conn)
        return web.json_response([UserSchema().dump(user_data) for user_data in users_list], status=200)


class UserDetailView(web.View):
    @docs(
        tags=['User'],
        summary='Get user data by id or login',
        description="This can only be done by authorized users. {slug} may be 'id' or 'login'",
        responses={
            200: {'description': 'Successful operation', 'schema': UserSchema},
            401: {'description': "You aren't authorized"},
            404: {'description': 'Not found'},
        },
    )
    @response_schema(UserSchema)
    async def get(self):
        """
        Get user data by id or login
        """
        await check_authorized(self.request)

        conn = self.request.app['conn']
        user = self.request.app['model']['user']

        slug = self.request.match_info['slug']
        user_data = await user.read(conn, slug)
        if not user_data:
            raise web.HTTPNotFound

        return web.json_response(UserSchema().dump(user_data), status=200)

    @docs(
        tags=['User'],
        summary='Update user by id or login',
        description="This can only be done by authorized users with admin permissions. {slug} may be 'id' or 'login'",
        responses={
            200: {'description': 'Successful operation', 'schema': UserSchema},
            400: {'description': 'Invalid data, update error'},
            401: {'description': "You aren't authorized"},
            403: {'description': "You haven't permissions"},
            422: {"description": "Validation error"},
        },
    )
    @request_schema(UserSchema(exclude=['id'], partial=True))
    @response_schema(UserSchema)
    async def patch(self):
        """
        Update user by id or login
        """
        await check_permission(self.request, 'admin')

        conn = self.request.app['conn']
        user = self.request.app['model']['user']

        slug = self.request.match_info['slug']
        user_data = self.request['data']
        updated_user = await user.update(conn, slug, user_data)
        if not updated_user:
            return web.json_response({'error': 'Update error'}, status=400)

        return web.json_response(UserSchema().dump(updated_user), status=200)

    @docs(
        tags=['User'],
        summary='Delete user by id or login',
        description="This can only be done by authorized users with admin permissions. {slug} may be 'id' or 'login'",
        responses={
            200: {'description': 'Successful operation'},
            400: {'description': 'Delete error'},
            401: {'description': "You aren't authorized"},
            403: {'description': "You haven't permissions"},
        },
    )
    async def delete(self):
        """
        Delete user by id or login
        """
        await check_permission(self.request, 'admin')

        conn = self.request.app['conn']
        user = self.request.app['model']['user']

        slug = self.request.match_info['slug']
        if not await user.delete(conn, slug):
            return web.json_response({'error': 'Delete error'}, status=400)

        return web.json_response(status=200)
