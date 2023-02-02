from aiohttp import web
from aiohttp_security import remember, forget, check_authorized, check_permission
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r201, r400, r401, r403, r404
from pydantic import ValidationError
from typing import Union

from srv.actions.authorization import check_credentials

from .validations import LoginModel, UserModel, UpdateUserModel


class CustomView(PydanticView):
    async def on_validation_error(self, exception: ValidationError, context: str):
        errors = exception.errors()
        custom_errors = {error['loc'][0]: [] for error in errors}
        for error in errors:
            custom_errors[error['loc'][0]].append(error['msg'])
        return web.json_response(data=custom_errors, status=400)


class LoginView(CustomView):
    async def post(self, data_model: LoginModel) -> Union[r200, r400]:
        """
        User session authorization.
        This can only be done by an unblocked users.

        Tags: Authorization
        Status Codes:
            200: Successful operation
            400: Invalid username/password combination or this user is blocked
        """
        data = data_model.dict()
        conn = self.request.app['conn']
        if not await check_credentials(conn, data):
            return web.json_response(
                {'error': 'Invalid username/password combination or this user is blocked'}, status=400
            )

        response = web.json_response(status=200)
        await remember(self.request, response, data['login'])
        return response


class LogoutView(CustomView):
    async def post(self) -> Union[r200, r401]:
        """
        Session terminate.
        This can only be done if you are authorized.

        Tags: Authorization
        Status Codes:
            200: Successful operation
            401: You aren't authorized
        """
        await check_authorized(self.request)

        response = web.json_response(status=200)
        await forget(self.request, response)
        return response


class UserView(CustomView):
    async def post(self, user_model: UserModel) -> Union[r201, r400, r401, r403]:
        """
        Create new user.
        This can only be done by authorized users with admin permissions.

        Tags: User
        Status Codes:
            201: Successful operation
            400: Invalid data, insert error
            401: You aren't authorized
            403: You haven't permissions
        """
        await check_permission(self.request, 'admin')

        user_data = user_model.dict(exclude_none=True)
        conn = self.request.app['conn']
        user = self.request.app['model']['user']
        created_user = await user.create(conn, user_data)
        if not created_user:
            return web.json_response({'error': 'Insert error'}, status=400)

        return web.json_response(created_user, status=201)

    async def get(self) -> Union[r200, r401]:
        """
        Get list of users.
        This can only be done by authorized users. Return null if users not found.

        Tags: User
        Status Codes:
            200: Successful operation, return list of users
            401: You aren't authorized
        """
        await check_authorized(self.request)

        conn = self.request.app['conn']
        user = self.request.app['model']['user']
        users_list = await user.read_all(conn)
        return web.json_response(users_list, status=200)


class OneUserView(CustomView):
    async def get(self, slug: str, /) -> Union[r200, r401, r404]:
        """
        Get user data by id or login.
        This can only be done by authorized users. {slug} may be 'id' or 'login'.

        Tags: User
        Status Codes:
            200: Successful operation
            401: You aren't authorized
            404: Not found
        """
        await check_authorized(self.request)

        conn = self.request.app['conn']
        user = self.request.app['model']['user']
        user_data = await user.read(conn, slug)
        if not user_data:
            raise web.HTTPNotFound

        return web.json_response(user_data, status=200)

    async def patch(self, slug: str, /, user_model: UpdateUserModel) -> Union[r200, r400, r401, r403]:
        """
        Update user by id or login.
        This can only be done by authorized users with admin permissions. {slug} may be 'id' or 'login'.

        Tags: User
        Status Codes:
            200: Successful operation
            400: Invalid data, update error
            401: You aren't authorized
            403: You haven't permissions
        """
        await check_permission(self.request, 'admin')

        user_data = user_model.dict(exclude_none=True)
        conn = self.request.app['conn']
        user = self.request.app['model']['user']
        updated_user = await user.update(conn, slug, user_data)
        if not updated_user:
            return web.json_response({'error': 'Update error'}, status=400)

        return web.json_response(updated_user, status=200)

    async def delete(self, slug: str, /) -> Union[r200, r400, r401, r403]:
        """
        Delete user by id or login.
        This can only be done by authorized users with admin permissions. {slug} may be 'id' or 'login'.

        Tags: User
        Status Codes:
            200: Successful operation
            400: Delete error
            401: You aren't authorized
            403: You haven't permissions
        """
        await check_permission(self.request, 'admin')

        conn = self.request.app['conn']
        user = self.request.app['model']['user']
        if not await user.delete(conn, slug):
            return web.json_response({'error': 'Delete error'}, status=400)

        return web.json_response(status=200)
