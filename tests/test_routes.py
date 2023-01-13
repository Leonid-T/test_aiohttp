import pytest
import asyncio

from tests.init_app import create_db_data, delete_db_data
from tests.tools import insert_block_user, json_validate_user, random_user_id, random_user_login
from tests.clients import client, client_admin, client_read


pytestmark = pytest.mark.asyncio


def setup_module(module):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db_data())


def teardown_module(module):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(delete_db_data())


async def test_login_with_admin(client):
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200


async def test_login_with_invalid_data_1(client):
    resp = await client.post('/login', json={
        'login11': 'admin',
        'password11': 'admin'
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_login_with_invalid_data_2(client):
    resp = await client.post('/login', json={
        'login': None,
        'password': None
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_login_with_block_permissions(client):
    login = 'test'
    password = 'test'
    await insert_block_user(client.conn, login, password)
    resp = await client.post('/login', json={
        'login': login,
        'password': password
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid username/password combination or this user is blocked'}


async def test_logout_with_admin(client_admin):
    resp = await client_admin.post('/logout')
    assert resp.status == 200


async def test_logout_without_login(client):
    resp = await client.post('/logout')
    assert resp.status == 401


async def test_create_user_with_admin(client_admin):
    resp = await client_admin.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200


async def test_create_user_without_login(client):
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': 'test',
        'date_of_birth': '1970-01-01',
    })
    assert resp.status == 401


async def test_create_user_with_read_permissions(client_read):
    resp = await client_read.post('/user', json={
        'name': 'test2',
        'surname': 'test2',
        'login': 'test2',
        'password': '12345',
        'date_of_birth': '1970-01-01',
    })
    assert resp.status == 403


async def test_create_user_with_invalid_data_1(client_admin):
    resp = await client_admin.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login1': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_create_user_with_invalid_data_2(client_admin):
    resp = await client_admin.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970_01_01',
        'permissions': 'read'
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_create_repeating_user(client_admin):
    resp = await client_admin.post('/user', json={
        'login': 'admin',
        'password': '12345',
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_read_user_list_with_admin(client_admin):
    resp = await client_admin.get('/user')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, list)
    for user in data:
        assert isinstance(user, dict)
        await json_validate_user(user)


async def test_read_user_list_without_login(client):
    resp = await client.get('/user')
    assert resp.status == 401


async def test_read_user_list_with_read_permissions(client_read):
    resp = await client_read.get('/user')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, list)
    for user in data:
        assert isinstance(user, dict)
        await json_validate_user(user)


async def test_read_user_with_admin_with_login_field(client_admin):
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.get(f'/user/{login}')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, dict)
    assert data['login'] == login
    await json_validate_user(data)


async def test_read_user_with_admin_with_id_field(client_admin):
    user_id = await random_user_id(client_admin.conn)
    resp = await client_admin.get(f'/user/{user_id}')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, dict)
    assert data['id'] == user_id
    await json_validate_user(data)


async def test_read_user_without_login(client):
    login = await random_user_login(client.conn)
    resp = await client.get(f'/user/{login}')
    assert resp.status == 401


async def test_read_user_with_read_permissions(client_read):
    login = await random_user_login(client_read.conn)
    resp = await client_read.get(f'/user/{login}')
    assert resp.status == 200
    data = await resp.json()
    assert isinstance(data, dict)
    assert data['login'] == login
    await json_validate_user(data)


async def test_read_non_exist_user(client_admin):
    resp = await client_admin.get('/user/non_exist')
    assert resp.status == 200
    data = await resp.json()
    assert data is None


async def test_update_user_with_admin_with_login_field(client_admin):
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


async def test_update_user_with_admin_with_id_field(client_admin):
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


async def test_update_user_without_login(client):
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
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_update_user_with_invalid_data_2(client_admin):
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.patch(f'/user/{login}', json={
        'date_of_birth': '1970_01_02',
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_delete_user_with_admin_with_login_field(client_admin):
    login = await random_user_login(client_admin.conn)
    resp = await client_admin.delete(f'/user/{login}')
    assert resp.status == 200


async def test_delete_user_with_admin_with_id_field(client_admin):
    user_id = await random_user_id(client_admin.conn)
    resp = await client_admin.delete(f'/user/{user_id}')
    assert resp.status == 200


async def test_delete_user_without_login(client):
    login = await random_user_login(client.conn)
    resp = await client.delete(f'/user/{login}')
    assert resp.status == 401


async def test_delete_user_with_read_permissions(client_read):
    login = await random_user_login(client_read.conn)
    resp = await client_read.delete(f'/user/{login}')
    assert resp.status == 403
