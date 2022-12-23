from abc import ABC, abstractmethod
import sqlalchemy as sa

from passlib.hash import sha256_crypt
from datetime import date

from . import db


class Model(ABC):
    @abstractmethod
    async def create(self, *args, **kwargs):
        pass

    @abstractmethod
    async def read(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    @abstractmethod
    async def delete(self, *args, **kwargs):
        pass


class User(Model):
    model = db.user
    engine = db.engine

    @classmethod
    async def create(cls, data):
        password = data.get('password')
        if not password:
            return True
        data['password'] = sha256_crypt.using().hash(password)
        if data.get('date_of_birth'):
            try:
                data['date_of_birth'] = date.fromisoformat(data['date_of_birth'])
            except ValueError:
                return True
        try:
            async with cls.engine.connect() as conn:
                await conn.execute(
                    cls.model.insert(), data
                )
                await conn.commit()
        except sa.exc.IntegrityError:
            return True

    @classmethod
    async def read(cls, slug):
        if slug.isdigit():
            where = cls.model.c.id == int(slug)
        else:
            where = cls.model.c.login == slug
        async with cls.engine.connect() as conn:
            ret = await conn.execute(
                cls.model.select().where(where)
            )
        row = ret.fetchone()
        if row:
            return await cls._create_user_from_row(row)

    @classmethod
    async def read_all(cls):
        async with cls.engine.connect() as conn:
            ret = await conn.execute(
                cls.model.select()
            )
        users = [await cls._create_user_from_row(row) for row in ret]
        return users

    @classmethod
    async def update(cls, slug, data):
        if data.get('password'):
            data['password'] = sha256_crypt.using().hash(data['password'])
        if data.get('date_of_birth'):
            try:
                data['date_of_birth'] = date.fromisoformat(data['date_of_birth'])
            except ValueError:
                return True
        if slug.isdigit():
            where = cls.model.c.id == int(slug)
        else:
            where = cls.model.c.login == slug
        try:
            async with cls.engine.connect() as conn:
                await conn.execute(
                    cls.model.update().values(data).where(where)
                )
                await conn.commit()
        except (sa.exc.ProgrammingError, sa.exc.CompileError):
            return True

    @classmethod
    async def delete(cls, slug):
        if slug.isdigit():
            where = cls.model.c.id == int(slug)
        else:
            where = cls.model.c.login == slug
        async with cls.engine.connect() as conn:
            await conn.execute(
                cls.model.delete().where(where)
            )
            await conn.commit()

    @classmethod
    async def _create_user_from_row(cls, row):
        return {
            'id': row[0],
            'name': row[1],
            'surname': row[2],
            'login': row[3],
            'password': row[4],
            'date_of_birth': str(row[5]),
            'permissions': row[6],
        }
