from jsonschema import validate


async def json_validate_login(json_data):
    schema = {
        'type': 'object',
        'properties': {
            'login': {'type': 'string'},
            'password': {'type': 'string'},
        },
        'required': ['login', 'password'],
        'additionalProperties': False,
    }
    validate(instance=json_data, schema=schema)


async def json_validate_create_user(json_data):
    schema = {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'name': {'type': 'string'},
            'surname': {'type': 'string'},
            'login': {'type': 'string'},
            'password': {'type': 'string'},
            'date_of_birth': {'type': 'string'},
            'permissions': {'type': 'string'},
        },
        'required': ['login', 'password'],
        'additionalProperties': False,
    }
    validate(instance=json_data, schema=schema)


async def json_validate_update_user(json_data):
    schema = {
        'type': 'object',
        'properties': {
            'id': {'type': 'number'},
            'name': {'type': 'string'},
            'surname': {'type': 'string'},
            'login': {'type': 'string'},
            'password': {'type': 'string'},
            'date_of_birth': {'type': 'string'},
            'permissions': {'type': 'string'},
        },
        'additionalProperties': False,
    }
    validate(instance=json_data, schema=schema)
