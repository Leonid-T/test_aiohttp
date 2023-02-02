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
    def should_not_be_numeric(cls, v):
        if v.isdigit():
            raise ValueError('this field should not be numeric')
        return v

    @validator('login', 'password', 'name', 'surname', 'date_of_birth')
    def should_not_be_empty(cls, v):
        if not v:
            raise ValueError('this field should not be empty')
        return v


class UpdateUserModel(UserModel):
    login: Annotated[str, Field(max_length=128)] = None
    password: str = None
