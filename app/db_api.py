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
    sub_model = db.permissions
    engine = db.engine

    @classmethod
    async def create(cls, data):
        await cls._set_password(data)
        if await cls._set_date_of_birth(data):
            return True
        if await cls._set_permissions(data):
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
                sa.select(
                    cls.model.c.id,
                    cls.model.c.name,
                    cls.model.c.surname,
                    cls.model.c.login,
                    cls.model.c.password,
                    cls.model.c.date_of_birth,
                    cls.sub_model.c.perm_name,
                ).where(sa.and_(cls.model.c.permissions == cls.sub_model.c.id, where))
            )
        row = ret.fetchone()
        if row:
            return await cls._create_user_from_row(row)

    @classmethod
    async def read_all(cls):
        async with cls.engine.connect() as conn:
            ret = await conn.execute(
                sa.select(
                    cls.model.c.id,
                    cls.model.c.name,
                    cls.model.c.surname,
                    cls.model.c.login,
                    cls.model.c.password,
                    cls.model.c.date_of_birth,
                    cls.sub_model.c.perm_name,
                ).where(cls.model.c.permissions == cls.sub_model.c.id)
            )
        users = [await cls._create_user_from_row(row) for row in ret]
        return users

    @classmethod
    async def update(cls, slug, data):
        await cls._set_password(data)
        if await cls._set_date_of_birth(data):
            return True
        if await cls._set_permissions(data):
            return True
        where = await cls._set_where(slug)
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
        where = await cls._set_where(slug)
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

    @classmethod
    async def _set_password(cls, data):
        if data.get('password'):
            data['password'] = sha256_crypt.using().hash(data['password'])

    @classmethod
    async def _set_date_of_birth(cls, data):
        if data.get('date_of_birth'):
            try:
                data['date_of_birth'] = date.fromisoformat(data['date_of_birth'])
            except ValueError:
                return True

    @classmethod
    async def _set_permissions(cls, data):
        if data.get('permissions'):
            perm = data['permissions']
            async with cls.engine.connect() as conn:
                id = await conn.scalar(
                    sa.select(cls.sub_model.c.id)
                    .where(cls.sub_model.c.perm_name == perm)
                )
            if id:
                data['permissions'] = id
            else:
                return True

    @classmethod
    async def _set_where(cls, slug):
        if slug.isdigit():
            return cls.model.c.id == int(slug)
        else:
            return cls.model.c.login == slug
