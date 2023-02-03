from pydantic import BaseModel, Field, Extra, validator
from datetime import date
from typing import Literal, Annotated


class LoginModel(BaseModel, extra=Extra.forbid):
    login: Annotated[str, Field(max_length=128)]
    password: str


class UserModel(BaseModel, extra=Extra.forbid):
    id: int = None
    name: Annotated[str, Field(max_length=32)] = None
    surname: Annotated[str, Field(max_length=32)] = None
    login: Annotated[str, Field(max_length=128)]
    password: str
    date_of_birth: date = None
    permissions: Literal['admin', 'read', 'block'] = None

    @validator('login', 'password')
    def should_not_be_null(cls, v):
        if v is None:
            raise ValueError('this field should not be null')
        return v

    @validator('login')
    def should_not_be_numeric(cls, v):
        if isinstance(v, str) and v.isdigit():
            raise ValueError('this field should not be numeric')
        return v

    @validator('login', 'password', 'name', 'surname')
    def should_not_be_empty(cls, v):
        if isinstance(v, str) and not v:
            raise ValueError('this field should not be empty')
        return v


class UpdateUserModel(UserModel):
    login: Annotated[str, Field(max_length=128)] = None
    password: str = None
