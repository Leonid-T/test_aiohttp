from aiohttp import web
from aiohttp_security import remember, forget, check_authorized, check_permission

from json.decoder import JSONDecodeError

from server.db.auth import check_credentials
from server.db.api import User


async def login(request):
    """
    Description end-point

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
    invalid_response = web.json_response(
        {'error': 'Invalid username/password combination or this user is blocked'}, status=400
    )
    try:
        data = await request.json()
    except JSONDecodeError:
        return invalid_response
    login = data.get('login')
    password = data.get('password')
    engine = request.app['db']

    if not (isinstance(login, str) and isinstance(password, str)):
        return invalid_response

    if await check_credentials(engine, login, password):
        response = web.json_response(status=200)
        await remember(request, response, login)
        return response

    return invalid_response


async def logout(request):
    """
    Description end-point

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
        Description end-point

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
            description: Invalid data
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
        await check_authorized(self.request)
        await check_permission(self.request, 'admin')
        invalid_response = web.json_response({'error': 'Invalid data'}, status=400)
        try:
            user_data = await self.request.json()
        except JSONDecodeError:
            return invalid_response

        engine = self.request.app['db']
        user = User(engine)
        error = await user.create(user_data)
        if error:
            return invalid_response

        return web.json_response(status=200)

    async def get(self):
        """
        Description end-point

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
        engine = self.request.app['db']
        user = User(engine)
        users_list = await user.read_all()
        return web.json_response(users_list, status=200)


class OneUserView(web.View):
    async def get(self):
        """
        Description end-point

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
        """
        await check_authorized(self.request)
        slug = self.request.match_info.get('slug')
        engine = self.request.app['db']
        user = User(engine)
        user_data = await user.read(slug)
        return web.json_response(user_data, status=200)

    async def patch(self):
        """
        Description end-point

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
            description: Invalid data
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
        await check_authorized(self.request)
        await check_permission(self.request, 'admin')
        invalid_response = web.json_response({'error': 'Invalid data'}, status=400)
        try:
            user_data = await self.request.json()
        except JSONDecodeError:
            return invalid_response

        slug = self.request.match_info.get('slug')
        engine = self.request.app['db']
        user = User(engine)
        error = await user.update(slug, user_data)
        if error:
            return invalid_response

        return web.json_response(status=200)

    async def delete(self):
        """
        Description end-point

        ---
        tags:
        - User
        summary: Delete user
        description: This can only be done by authorized users with admin permissions. {slug} may be 'id' or 'login'
        operationId: delete_user
        responses:
          '200':
            description: successful operation
          '401':
            description: you aren't authorized
          '403':
            description: you haven't permissions
        """
        await check_authorized(self.request)
        await check_permission(self.request, 'admin')
        slug = self.request.match_info.get('slug')
        engine = self.request.app['db']
        user = User(engine)
        await user.delete(slug)
        return web.json_response(status=200)
