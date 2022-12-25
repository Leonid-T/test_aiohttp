import pytest

from tests.init_app import get_app


pytestmark = pytest.mark.asyncio


async def test_login_with_admin(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200


async def test_login_with_invalid_data_1(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login11': 'admin',
        'password11': 'admin'
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid username/password combination or this user is blocked'}


async def test_login_with_invalid_data_2(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': None,
        'password': None
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid username/password combination or this user is blocked'}


async def test_login_with_block_permissions(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'login': 'test',
        'password': '12345',
        'permissions': 'block'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200
    resp = await client.post('/login', json={
        'login': 'test',
        'password': '12345'
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid username/password combination or this user is blocked'}


async def test_logout_with_admin(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200


async def test_logout_without_login(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/logout')
    assert resp.status == 401


async def test_create_user_with_admin(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200


async def test_create_user_without_login(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
    })
    assert resp.status == 401


async def test_create_user_with_read_permissions(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'login': 'test',
        'password': '12345',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200
    resp = await client.post('/login', json={
        'login': 'test',
        'password': '12345'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test2',
        'surname': 'test2',
        'login': 'test2',
        'password': '12345',
        'date_of_birth': '1970-01-01',
    })
    assert resp.status == 403


async def test_create_user_with_invalid_data_1(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
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


async def test_create_user_with_invalid_data_2(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
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


async def test_create_repeating_user(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'login': 'admin',
        'password': '12345',
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_read_user_list_with_admin(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.get('/user')
    assert resp.status == 200
    data = await resp.json()
    assert data == [
        {
            'id': 1,
            'name': 'admin',
            'surname': 'admin',
            'login': 'admin',
            'password': data[0]['password'],
            'date_of_birth': '1970-01-01',
            'permissions': 'admin',
        }
    ]


async def test_read_user_list_without_login(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.get('/user')
    assert resp.status == 401


async def test_read_user_list_with_read_permissions(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200
    resp = await client.post('/login', json={
        'login': 'test',
        'password': '12345'
    })
    assert resp.status == 200
    resp = await client.get('/user')
    assert resp.status == 200
    data = await resp.json()
    assert data == [
        {
            'id': 1,
            'name': 'admin',
            'surname': 'admin',
            'login': 'admin',
            'password': data[0]['password'],
            'date_of_birth': '1970-01-01',
            'permissions': 'admin',
        },
        {
            'id': 2,
            'name': 'test',
            'surname': 'test',
            'login': 'test',
            'password': data[1]['password'],
            'date_of_birth': '1970-01-01',
            'permissions': 'read'
        }
    ]


async def test_read_user_with_admin_with_login_field(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.get('/user/admin')
    assert resp.status == 200
    data = await resp.json()
    assert data == {
        'id': 1,
        'name': 'admin',
        'surname': 'admin',
        'login': 'admin',
        'password': data['password'],
        'date_of_birth': '1970-01-01',
        'permissions': 'admin',
    }


async def test_read_user_with_admin_with_id_field(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.get('/user/1')
    assert resp.status == 200
    data = await resp.json()
    assert data == {
        'id': 1,
        'name': 'admin',
        'surname': 'admin',
        'login': 'admin',
        'password': data['password'],
        'date_of_birth': '1970-01-01',
        'permissions': 'admin',
    }


async def test_read_user_without_login(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.get('/user/admin')
    assert resp.status == 401


async def test_read_user_with_read_permissions(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200
    resp = await client.post('/login', json={
        'login': 'test',
        'password': '12345'
    })
    assert resp.status == 200
    resp = await client.get('/user/test')
    assert resp.status == 200
    data = await resp.json()
    assert data == {
        'id': 2,
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': data['password'],
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    }


async def test_read_non_exist_user(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.get('/user/non_exist')
    assert resp.status == 200
    data = await resp.json()
    assert data is None


async def test_update_user_with_admin_with_login_field(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.patch('/user/test', json={
        'name': 'test1',
        'surname': 'test1',
        'login': 'test1',
        'password': '123456',
        'date_of_birth': '1970-01-02',
        'permissions': 'admin'
    })
    assert resp.status == 200


async def test_update_user_with_admin_with_id_field(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.patch('/user/2', json={
        'name': 'test1',
        'surname': 'test1',
        'login': 'test1',
        'password': '123456',
        'date_of_birth': '1970-01-02',
        'permissions': 'admin'
    })
    assert resp.status == 200


async def test_update_user_without_login(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200
    resp = await client.patch('/user/test', json={
        'name': 'test1',
        'surname': 'test1',
        'login': 'test1',
        'password': '123456',
        'date_of_birth': '1970-01-02',
        'permissions': 'admin'
    })
    assert resp.status == 401


async def test_update_user_with_read_permissions(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200
    resp = await client.post('/login', json={
        'login': 'test',
        'password': '12345'
    })
    assert resp.status == 200
    resp = await client.patch('/user/test', json={
        'name': 'test1',
        'surname': 'test1',
        'login': 'test1',
        'password': '123456',
        'date_of_birth': '1970-01-02',
        'permissions': 'admin'
    })
    assert resp.status == 403


async def test_update_user_with_invalid_data_1(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.patch('/user/test', json={
        'name1': 'test1',
        'surname1': 'test1',
        'login1': 'test1',
        'password1': '123456',
        'date_of_birth1': '1970-01-02',
        'permissions1': 'admin'
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_update_user_with_invalid_data_2(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.patch('/user/test', json={
        'date_of_birth': '1970_01_02',
    })
    assert resp.status == 400
    data = await resp.json()
    assert data == {'error': 'Invalid data'}


async def test_delete_user_with_admin_with_login_field(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.delete('/user/test')
    assert resp.status == 200
    resp = await client.get('/user/test')
    assert resp.status == 200
    data = await resp.json()
    assert data is None


async def test_delete_user_with_admin_with_id_field(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.delete('/user/2')
    assert resp.status == 200
    resp = await client.get('/user/2')
    assert resp.status == 200
    data = await resp.json()
    assert data is None


async def test_delete_user_without_login(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test',
        'surname': 'test',
        'login': 'test',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200
    resp = await client.delete('/user/test')
    assert resp.status == 401


async def test_delete_user_with_read_permissions(aiohttp_client):
    client = await aiohttp_client(await get_app())
    resp = await client.post('/login', json={
        'login': 'admin',
        'password': 'admin'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'login': 'test',
        'password': '12345',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.post('/user', json={
        'name': 'test1',
        'surname': 'test1',
        'login': 'test1',
        'password': '12345',
        'date_of_birth': '1970-01-01',
        'permissions': 'read'
    })
    assert resp.status == 200
    resp = await client.post('/logout')
    assert resp.status == 200
    resp = await client.post('/login', json={
        'login': 'test',
        'password': '12345'
    })
    assert resp.status == 200
    resp = await client.delete('/user/test1')
    assert resp.status == 403
