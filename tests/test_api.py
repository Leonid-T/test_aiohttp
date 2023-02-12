import pytest

from tests.tools import (
    insert_user, insert_random_user, filing_db_table_user, random_text, random_date, random_permissions,
    validate_user_initial_data, validate_user_db_data, check_deletion,
)
from tests.fixtures import alembic_engine, alembic_config, alembic_upgrade_downgrade, create_def_data
from tests.clients import client, auth_admin, auth_read


pytestmark = pytest.mark.asyncio


async def test_login_with_admin(client):
    """
    Default admin authorization should be successful
    """
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin',
    })
    assert resp.status == 200


async def test_login_with_invalid_data_1(client):
    """
    Authorization with invalid data should fail 422
    """
    resp = await client.post('/login', json={
        'login11': 'admin',  # invalid login field
        'password11': 'admin',  # invalid password field
    })
    assert resp.status == 422


async def test_login_with_invalid_data_2(client):
    """
    Authorization with invalid data should fail 422
    """
    resp = await client.post('/login', json={
        'login': None,  # invalid login field
        'password': None,  # invalid password field
    })
    assert resp.status == 422


async def test_login_with_read_permissions(client):
    """
    User authorization with read permissions should be successful
    """
    user_data = {
        'login': random_text(),
        'password': random_text(),
        'permissions': 'read',
    }
    await insert_user(client.conn, user_data)

    resp = await client.post('/login', json={
        'login': user_data['login'],
        'password': user_data['password'],
    })
    assert resp.status == 200


async def test_login_with_block_permissions(client):
    """
    User authorization with block permissions should fail 400
    """
    user_data = {
        'login': random_text(),
        'password': random_text(),
        'permissions': 'block',
    }
    await insert_user(client.conn, user_data)

    resp = await client.post('/login', json={
        'login': user_data['login'],
        'password': user_data['password'],
    })
    assert resp.status == 400

    returned_data = await resp.json()
    assert returned_data == {'error': 'Invalid username/password combination or this user is blocked'}


async def test_logout_with_admin(client, auth_admin):
    """
    Authorized user logout should be successful
    """
    resp = await client.post('/logout')
    assert resp.status == 200


async def test_logout_without_login(client):
    """
    Unauthorized user logout should fail 401
    """
    resp = await client.post('/logout')
    assert resp.status == 401


async def test_create_user_with_admin(client, auth_admin):
    """
    Creating user with administrator should be successful
    """
    user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(),
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }
    resp = await client.post('/user', json=user_data)
    assert resp.status == 201

    returned_data = await resp.json()
    await validate_user_initial_data(user_data, returned_data)
    await validate_user_db_data(client.conn, returned_data)


async def test_create_user_without_login(client):
    """
    Creating user with unauthorized should fail 401
    """
    user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(),
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }
    resp = await client.post('/user', json=user_data)
    assert resp.status == 401


async def test_create_user_with_read_permissions(client, auth_read):
    """
    Creating user with a user with read permissions should fail 403
    """
    user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(),
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }
    resp = await client.post('/user', json=user_data)
    assert resp.status == 403


async def test_create_user_with_invalid_data_1(client, auth_admin):
    """
    Creating user with invalid data should fail 422
    """
    user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login1': random_text(),  # invalid login field
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }
    resp = await client.post('/user', json=user_data)
    assert resp.status == 422


async def test_create_user_with_invalid_data_2(client, auth_admin):
    """
    Creating user with invalid data should fail 422
    """
    user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(),
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': 'other',  # invalid permissions field
    }
    resp = await client.post('/user', json=user_data)
    assert resp.status == 422


async def test_create_repeating_user(client, auth_admin):
    """
    Creating a repeating user should fail 400
    """
    user_data = await insert_random_user(client.conn)

    resp = await client.post('/user', json={
        'login': user_data['login'],  # repeating login field
        'password': random_text(),
    })
    assert resp.status == 400


async def test_read_user_list_with_admin(client, auth_admin):
    """
    Reading user list with administrator should be successful
    """
    await filing_db_table_user(client.conn)

    resp = await client.get('/user')
    assert resp.status == 200

    returned_data = await resp.json()
    for user in returned_data:
        await validate_user_db_data(client.conn, user)


async def test_read_user_list_without_login(client):
    """
    Reading user list with unauthorized should fail 401
    """
    await filing_db_table_user(client.conn)

    resp = await client.get('/user')
    assert resp.status == 401


async def test_read_user_list_with_read_permissions(client, auth_read):
    """
    Reading user list with a user with read permissions should be successful
    """
    await filing_db_table_user(client.conn)

    resp = await client.get('/user')
    assert resp.status == 200

    returned_data = await resp.json()
    for user in returned_data:
        await validate_user_db_data(client.conn, user)


async def test_read_user_with_admin_by_login(client, auth_admin):
    """
    Reading user by login with administrator should be successful
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    resp = await client.get(f'/user/{login}')
    assert resp.status == 200

    returned_data = await resp.json()
    assert returned_data['login'] == login
    await validate_user_db_data(client.conn, returned_data)


async def test_read_user_with_admin_by_id(client, auth_admin):
    """
    Reading user by id with administrator should be successful
    """
    user_data = await insert_random_user(client.conn)
    user_id = user_data['id']

    resp = await client.get(f'/user/{user_id}')
    assert resp.status == 200

    returned_data = await resp.json()
    assert returned_data['id'] == user_id
    await validate_user_db_data(client.conn, returned_data)


async def test_read_user_without_login(client):
    """
    Reading user with unauthorized should fail 401
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    resp = await client.get(f'/user/{login}')
    assert resp.status == 401


async def test_read_user_with_read_permissions(client, auth_read):
    """
    Reading user with a user with read permissions should be successful
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    resp = await client.get(f'/user/{login}')
    assert resp.status == 200

    returned_data = await resp.json()
    assert returned_data['login'] == login
    await validate_user_db_data(client.conn, returned_data)


async def test_read_non_existent_user(client, auth_admin):
    """
    Reading non-existent user should be fail 404
    """
    resp = await client.get('/user/non_exist')
    assert resp.status == 404


async def test_update_user_with_admin_by_login(client, auth_admin):
    """
    Updating user by login with administrator should be successful
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    update_user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(6),  # ensure unique login field
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }

    resp = await client.patch(f'/user/{login}', json=update_user_data)
    assert resp.status == 200

    returned_data = await resp.json()
    await validate_user_initial_data(update_user_data, returned_data)
    await validate_user_db_data(client.conn, returned_data)


async def test_update_user_with_admin_by_id(client, auth_admin):
    """
    Updating user by id with administrator should be successful
    """
    user_data = await insert_random_user(client.conn)
    user_id = user_data['id']

    update_user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(6),  # ensure unique login field
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }

    resp = await client.patch(f'/user/{user_id}', json=update_user_data)
    assert resp.status == 200

    returned_data = await resp.json()
    await validate_user_initial_data(update_user_data, returned_data)
    await validate_user_db_data(client.conn, returned_data)


async def test_update_user_without_login(client):
    """
    Updating user with unauthorized should fail 401
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    update_user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(6),  # ensure unique login field
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }

    resp = await client.patch(f'/user/{login}', json=update_user_data)
    assert resp.status == 401


async def test_update_user_with_read_permissions(client, auth_read):
    """
    Updating user with a user with read permissions should fail 403
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    update_user_data = {
        'name': random_text(),
        'surname': random_text(),
        'login': random_text(6),  # ensure unique login field
        'password': random_text(),
        'date_of_birth': random_date(),
        'permissions': random_permissions(),
    }

    resp = await client.patch(f'/user/{login}', json=update_user_data)
    assert resp.status == 403


async def test_update_user_with_invalid_data_1(client, auth_admin):
    """
    Updating user with invalid data should fail 422
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    update_user_data = {
        'date_of_birth': '2000_15_15',  # invalid date_of_birth field
    }

    resp = await client.patch(f'/user/{login}', json=update_user_data)
    assert resp.status == 422


async def test_update_user_with_invalid_data_2(client, auth_admin):
    """
    Updating user with invalid data should fail 422
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    update_user_data = {
        'permissions': 'other',  # invalid permissions field
    }

    resp = await client.patch(f'/user/{login}', json=update_user_data)
    assert resp.status == 422


async def test_delete_user_with_admin_by_login(client, auth_admin):
    """
    Deleting user by login with administrator should be successful
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    resp = await client.delete(f'/user/{login}')
    assert resp.status == 200

    await check_deletion(client.conn, login)


async def test_delete_user_with_admin_by_id(client, auth_admin):
    """
    Deleting user by id with administrator should be successful
    """
    user_data = await insert_random_user(client.conn)
    user_id = user_data['id']

    resp = await client.delete(f'/user/{user_id}')
    assert resp.status == 200

    await check_deletion(client.conn, user_data['login'])


async def test_delete_non_existent_user(client, auth_admin):
    """
    Deleting non-existent user should be fail 400
    """
    resp = await client.delete('/user/non_exist')
    assert resp.status == 400

    data = await resp.json()
    assert data == {'error': 'Delete error'}


async def test_delete_user_without_login(client):
    """
    Deleting user with unauthorized should fail 401
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    resp = await client.delete(f'/user/{login}')
    assert resp.status == 401


async def test_delete_user_with_read_permissions(client, auth_read):
    """
    Deleting user with a user with read permissions should fail 403
    """
    user_data = await insert_random_user(client.conn)
    login = user_data['login']

    resp = await client.delete(f'/user/{login}')
    assert resp.status == 403


async def test_api_documentation(client):
    """
    Api documentation should be available by url from the config['docs_url']
    """
    docs_url = client.app['config']['docs_url']
    resp = await client.get(docs_url)
    assert resp.status == 200
