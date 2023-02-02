import pytest
import asyncio

from tests.init_app import create_db_data, delete_db_data
from tests.tools import insert_user, json_validate_user, random_user_id, random_user_login
from tests.clients import client, client_admin, client_read


pytestmark = pytest.mark.asyncio


def setup_module(module):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db_data())


def teardown_module(module):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_db_data())


async def test_login_with_admin(client):
    """
    Default admin authorization should be successful.
    """
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200


async def test_login_with_invalid_data_1(client):
    """
    Authorization with invalid data should fail 400.
    """
    resp = await client.post('/login', json={
        'login11': 'admin',
        'password11': 'admin'
    })
    assert resp.status == 400


async def test_login_with_invalid_data_2(client):
    """
    Authorization with invalid data should fail 400.
    """
    resp = await client.post('/login', json={
        'login': None,
        'password': None
    })
    assert resp.status == 400


async def test_login_with_read_permissions(client):
    """
    User authorization with read permissions should be successful.
    """
    login = 'test'
    password = 'test'
    await insert_user(client.conn, login, password, 'read')
    resp = await client.post('/login', json={
        'login': login,
        'password': password
    })
    assert resp.status == 200


async def test_login_with_block_permissions(client):
    """
    User authorization with block permissions should fail 400.
    """
    login = 'test'
    password = 'test'
    await insert_user(client.conn, login, password, 'block')
    resp = await client.post('/login', json={
        'login': login,
        'password': password
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid username/password combination or this user is blocked'}


async def test_logout_with_admin(client_admin):
    """
    Authorized user logout should be successful.
    """
    resp = await client_admin.post('/logout')
    assert resp.status == 200


async def test_logout_without_login(client):
    """
    Unauthorized user logout should fail 401.
    """
    resp = await client.post('/logout')
    assert resp.status == 401


async def test_create_user_with_admin(client_admin):
    """
    Creating user with administrator should be successful.
    """
    resp = await client_admin.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 201
    data = await resp.json()
    assert isinstance(data, dict)
    await json_validate_user(data)


async def test_create_user_without_login(client):
    """
    Creating user with unauthorized should fail 401.
    """
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-01',
    })
    assert resp.status == 401


async def test_create_user_with_read_permissions(client_read):
    """
    Creating user with a user with read permissions should fail 403.
    """
    resp = await client_read.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-01',
    })
    assert resp.status == 403


async def test_create_user_with_invalid_data_1(client_admin):
    """
    Creating user with invalid data should fail 400.
    """
    resp = await client_admin.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login1': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 400


async def test_create_user_with_invalid_data_2(client_admin):
    """
    Creating user with invalid data should fail 400.
    """
    resp = await client_admin.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-01',
        'permissions': 'other'
    })
    assert resp.status == 400


async def test_create_repeating_user(client_admin):
    """
    Creating a repeating user should fail 400.
    """
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.post('/user', json={
        'login': login,
        'password': 'test',
    })
    assert resp.status == 400


async def test_read_user_list_with_admin(client_admin):
    """
    Reading user list with administrator should be successful.
    """
    resp = await client_admin.get('/user')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, list)
    for user in data:
        assert isinstance(user, dict)
        await json_validate_user(user)


async def test_read_user_list_without_login(client):
    """
    Reading user list with unauthorized should fail 401.
    """
    resp = await client.get('/user')
    assert resp.status == 401


async def test_read_user_list_with_read_permissions(client_read):
    """
    Reading user list with a user with read permissions should be successful.
    """
    resp = await client_read.get('/user')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, list)
    for user in data:
        assert isinstance(user, dict)
        await json_validate_user(user)


async def test_read_user_with_admin_by_login(client_admin):
    """
    Reading user by login with administrator should be successful.
    """
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.get(f'/user/{login}')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, dict)
    assert data['login'] == login
    await json_validate_user(data)


async def test_read_user_with_admin_by_id(client_admin):
    """
    Reading user by id with administrator should be successful.
    """
    user_id = await random_user_id(client_admin.conn)
    resp = await client_admin.get(f'/user/{user_id}')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, dict)
    assert data['id'] == user_id
    await json_validate_user(data)


async def test_read_user_without_login(client):
    """
    Reading user with unauthorized should fail 401.
    """
    login = await random_user_login(client.conn)
    resp = await client.get(f'/user/{login}')
    assert resp.status == 401


async def test_read_user_with_read_permissions(client_read):
    """
    Reading user with a user with read permissions should be successful.
    """
    login = await random_user_login(client_read.conn)
    resp = await client_read.get(f'/user/{login}')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, dict)
    assert data['login'] == login
    await json_validate_user(data)


async def test_read_non_existent_user(client_admin):
    """
    Reading non-existent user should be fail 404.
    """
    resp = await client_admin.get('/user/non_exist')
    assert resp.status == 404


async def test_update_user_with_admin_by_login(client_admin):
    """
    Updating user by login with administrator should be successful.
    """
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.patch(f'/user/{login}', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-02',
        'permissions': 'admin'
    })
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, dict)
    await json_validate_user(data)


async def test_update_user_with_admin_by_id(client_admin):
    """
    Updating user by id with administrator should be successful.
    """
    user_id = await random_user_id(client_admin.conn)
    resp = await client_admin.patch(f'/user/{user_id}', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-02',
        'permissions': 'admin'
    })
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, dict)
    await json_validate_user(data)


async def test_update_user_without_login(client):
    """
    Updating user with unauthorized should fail 401.
    """
    login = await random_user_login(client.conn)
    resp = await client.patch(f'/user/{login}', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-02',
        'permissions': 'admin'
    })
    assert resp.status == 401


async def test_update_user_with_read_permissions(client_read):
    """
    Updating user with a user with read permissions should fail 403.
    """
    login = await random_user_login(client_read.conn)
    resp = await client_read.patch(f'/user/{login}', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-02',
        'permissions': 'admin'
    })
    assert resp.status == 403


async def test_update_user_with_invalid_data_1(client_admin):
    """
    Updating user with invalid data should fail 400.
    """
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.patch(f'/user/{login}', json={
        'name1': 'test',
        'surname1': 'test',
        'login1': 'test',
        'password1': 'test',
        'date_of_birth1': '1970-01-02',
        'permissions1': 'admin'
    })
    assert resp.status == 400


async def test_update_user_with_invalid_data_2(client_admin):
    """
    Updating user with invalid data should fail 400.
    """
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.patch(f'/user/{login}', json={
        'permissions': 'other',
    })
    assert resp.status == 400


async def test_delete_user_with_admin_by_login(client_admin):
    """
    Deleting user by login with administrator should be successful.
    """
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.delete(f'/user/{login}')
    assert resp.status == 200


async def test_delete_user_with_admin_by_id(client_admin):
    """
    Deleting user by id with administrator should be successful.
    """
    user_id = await random_user_id(client_admin.conn)
    resp = await client_admin.delete(f'/user/{user_id}')
    assert resp.status == 200


async def test_delete_non_existent_user(client_admin):
    """
    Deleting non-existent user should be fail 400.
    """
    resp = await client_admin.delete('/user/non_exist')
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Delete error'}


async def test_delete_user_without_login(client):
    """
    Deleting user with unauthorized should fail 401.
    """
    login = await random_user_login(client.conn)
    resp = await client.delete(f'/user/{login}')
    assert resp.status == 401


async def test_delete_user_with_read_permissions(client_read):
    """
    Deleting user with a user with read permissions should fail 403.
    """
    login = await random_user_login(client_read.conn)
    resp = await client_read.delete(f'/user/{login}')
    assert resp.status == 403


async def test_api_documentation(client):
    """
    Api documentation should be available by url from the config['docs_url']
    """
    docs_url = client.app['config']['docs_url']
    resp = await client.get(docs_url)
    assert resp.status == 200
