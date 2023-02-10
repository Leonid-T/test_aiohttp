from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    """
    User session authorization schema
    """
    login = fields.Str(
        validate=validate.And(validate.Length(min=1, max=128), lambda v: not str.isdigit(v)), required=True
    )
    password = fields.Str(validate=validate.Length(min=1), required=True)


class UserSchema(Schema):
    """
    User response schema
    """
    id = fields.Int()
    name = fields.Str(validate=validate.Length(min=1, max=32), allow_none=True)
    surname = fields.Str(validate=validate.Length(min=1, max=32), allow_none=True)
    login = fields.Str(validate=validate.And(validate.Length(min=1, max=128), lambda v: not str.isdigit(v)))
    password = fields.Str(validate=validate.Length(min=1))
    date_of_birth = fields.Date(allow_none=True)
    permissions = fields.Str(validate=validate.OneOf(('admin', 'read', 'block')))

    class Meta:
        ordered = True


class UserCreateSchema(LoginSchema, UserSchema):
    """
    Create new user schema
    """
    class Meta:
        exclude = ['id']
