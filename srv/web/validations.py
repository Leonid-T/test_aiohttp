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

    @validator('login')
    def login_should_not_be_numeric(cls, v):
        if v.isdigit():
            raise ValueError('login should not be numeric')
        return v

    @validator('login')
    def login_should_not_be_empty(cls, v):
        if not v:
            raise ValueError('login should not be empty')
        return v

    @validator('password')
    def password_should_not_be_empty(cls, v):
        if not v:
            raise ValueError('password should not be empty')
        return v


class UpdateUserModel(UserModel):
    login: Annotated[str, Field(max_length=128)] = None
    password: str = None
