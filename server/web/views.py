from aiohttp import web
from aiohttp_security import remember, forget, check_authorized, check_permission

from server.store.pg.auth import check_credentials
from server.store.pg.api import User

from .validations import json_validate_login, json_validate_create_user, json_validate_update_user


async def login(request):
    """
    User session authorization.

    ---
    tags:
    - Authorization
    summary: User login
    description: This can only be done by an unblocked users.
    operationId: login
    produces:
    - application/json
    parameters:
    - in: body
      name: body
      description: User authorization
      required: false
      schema:
        type: object
        properties:
          login:
            type: string
          password:
            type: string
    responses:
      '200':
        description: successful operation
      '400':
        description: Invalid username/password combination or this user is blocked
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = await request.json()
    await json_validate_login(data)

    conn = request.app['conn']
    if not await check_credentials(conn, data):
        return web.json_response(
            {'error': 'Invalid username/password combination or this user is blocked'}, status=400
        )

    response = web.json_response(status=200)
    await remember(request, response, data['login'])
    return response


async def logout(request):
    """
    Session terminate.

    ---
    tags:
    - Authorization
    summary: User logout
    description: This can only be done if you are authorized.
    operationId: logout
    responses:
      '200':
        description: successful operation
      '401':
        description: you aren't authorized
    """
    await check_authorized(request)

    response = web.json_response(status=200)
    await forget(request, response)
    return response


class UserView(web.View):
    async def post(self):
        """
        Create new user.

        ---
        tags:
        - User
        summary: Create user
        description: This can only be done by authorized users with admin permissions.
        operationId: create_user
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Create new user; date_of_birth format 'YYYY-MM-DD'; permissions may be 'block', 'admin' or 'read'
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
                format: string32
              surname:
                type: string
                format: string32
              login:
                type: string
                format: string128
              password:
                type: string
              date_of_birth:
                type: date
                format: iso
              permissions:
                type: string
                format: block, admin, read
        responses:
          '200':
            description: successful operation
          '400':
            description: Invalid data, insert error
            schema:
              type: object
              properties:
                error:
                  type: string
          '401':
            description: you aren't authorized
          '403':
            description: you haven't permissions
        """
        await check_permission(self.request, 'admin')

        user_data = await self.request.json()
        await json_validate_create_user(user_data)

        conn = self.request.app['conn']
        user = User()
        if not await user.create(conn, user_data):
            return web.json_response({'error': 'Insert error'}, status=400)

        return web.json_response(status=200)

    async def get(self):
        """
        Get list of users.

        ---
        tags:
        - User
        summary: Read all users
        description: This can only be done by authorized users. Return null if users not found.
        operationId: read_user_all
        responses:
          '200':
            description: successful operation, return list of users
            schema:
              type: object
              properties:
                id:
                  type: int
                name:
                  type: string
                  format: string32
                surname:
                  type: string
                  format: string32
                login:
                  type: string
                  format: string128
                password:
                  type: string
                date_of_birth:
                  type: date
                  format: iso
                permissions:
                  type: string
                  format: block, admin, read
          '401':
            description: you aren't authorized
        """
        await check_authorized(self.request)

        conn = self.request.app['conn']
        user = User()
        users_list = await user.read_all(conn)
        return web.json_response(users_list, status=200)


class OneUserView(web.View):
    async def get(self):
        """
        Get user data by id or login.

        ---
        tags:
        - User
        summary: Read user
        description: This can only be done by authorized users. {slug} may be 'id' or 'login'. Return null if user not found.
        operationId: read_user
        responses:
          '200':
            description: successful operation
            schema:
              type: object
              properties:
                id:
                  type: int
                name:
                  type: string
                  format: string32
                surname:
                  type: string
                  format: string32
                login:
                  type: string
                  format: string128
                password:
                  type: string
                date_of_birth:
                  type: date
                  format: iso
                permissions:
                  type: string
                  format: block, admin, read
          '401':
            description: you aren't authorized
          '404':
            description: not found
        """
        await check_authorized(self.request)

        slug = self.request.match_info.get('slug')

        conn = self.request.app['conn']
        user = User()
        user_data = await user.read(conn, slug)
        if not user_data:
            raise web.HTTPNotFound

        return web.json_response(user_data, status=200)

    async def patch(self):
        """
        Update user by id or login.

        ---
        tags:
        - User
        summary: Update user
        description: This can only be done by authorized users with admin permissions. {slug} may be 'id' or 'login'
        operationId: update_user
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Update user; date_of_birth format 'YYYY-MM-DD'; permissions may be 'block', 'admin' or 'read'
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
                format: string32
              surname:
                type: string
                format: string32
              login:
                type: string
                format: string128
              password:
                type: string
              date_of_birth:
                type: date
                format: iso
              permissions:
                type: string
                format: block, admin, read
        responses:
          '200':
            description: successful operation
          '400':
            description: Invalid data, update error
            schema:
              type: object
              properties:
                error:
                  type: string
          '401':
            description: you aren't authorized
          '403':
            description: you haven't permissions
        """
        await check_permission(self.request, 'admin')

        user_data = await self.request.json()
        await json_validate_update_user(user_data)

        slug = self.request.match_info.get('slug')
        conn = self.request.app['conn']
        user = User()
        if not await user.update(conn, slug, user_data):
            return web.json_response({'error': 'Update error'}, status=400)

        return web.json_response(status=200)

    async def delete(self):
        """
        Delete user by id or login.

        ---
        tags:
        - User
        summary: Delete user
        description: This can only be done by authorized users with admin permissions. {slug} may be 'id' or 'login'
        operationId: delete_user
        responses:
          '200':
            description: successful operation
          '400':
            description: delete error
          '401':
            description: you aren't authorized
          '403':
            description: you haven't permissions
        """
        await check_permission(self.request, 'admin')

        slug = self.request.match_info.get('slug')
        conn = self.request.app['conn']
        user = User()
        if not await user.delete(conn, slug):
            return web.json_response({'error': 'Delete error'}, status=400)

        return web.json_response(status=200)
