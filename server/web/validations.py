from pydantic import BaseModel, Field, Extra, validator
from datetime import date
from typing import Literal, Annotated


class LoginModel(BaseModel, extra=Extra.forbid):
    login: Annotated[str, Field(max_length=128)]
    password: str


class CreateUserModel(BaseModel, extra=Extra.forbid):
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


class UpdateUserModel(CreateUserModel):
    login: Annotated[str, Field(max_length=128)] = None
    password: str = None
