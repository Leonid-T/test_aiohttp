import sqlalchemy as sa

from passlib.hash import sha256_crypt
from datetime import date

from . import models


class User:
    model = models.user
    sub_model = models.permissions

    def __init__(self, engine):
        self.engine = engine

    async def create(self, data):
        await self._set_password(data)
        if await self._set_date_of_birth(data):
            return True
        if await self._set_permissions(data):
            return True
        try:
            async with self.engine.connect() as conn:
                await conn.execute(
                    self.model.insert(), data
                )
                await conn.commit()
        except sa.exc.IntegrityError:
            return True

    async def read(self, slug):
        where = await self._set_where(slug)
        async with self.engine.connect() as conn:
            ret = await conn.execute(
                sa.select(
                    self.model.c.id,
                    self.model.c.name,
                    self.model.c.surname,
                    self.model.c.login,
                    self.model.c.password,
                    self.model.c.date_of_birth,
                    self.sub_model.c.perm_name,
                ).where(sa.and_(self.model.c.permissions == self.sub_model.c.id, where))
            )
        row = ret.fetchone()
        if row:
            return await self._create_user_from_row(row)

    async def read_all(self):
        async with self.engine.connect() as conn:
            ret = await conn.execute(
                sa.select(
                    self.model.c.id,
                    self.model.c.name,
                    self.model.c.surname,
                    self.model.c.login,
                    self.model.c.password,
                    self.model.c.date_of_birth,
                    self.sub_model.c.perm_name,
                ).where(self.model.c.permissions == self.sub_model.c.id)
            )
        users = [await self._create_user_from_row(row) for row in ret]
        return users

    async def update(self, slug, data):
        await self._set_password(data)
        if await self._set_date_of_birth(data):
            return True
        if await self._set_permissions(data):
            return True
        where = await self._set_where(slug)
        try:
            async with self.engine.connect() as conn:
                await conn.execute(
                    self.model.update().values(data).where(where)
                )
                await conn.commit()
        except (sa.exc.ProgrammingError, sa.exc.CompileError):
            return True

    async def delete(self, slug):
        where = await self._set_where(slug)
        async with self.engine.connect() as conn:
            await conn.execute(
                self.model.delete().where(where)
            )
            await conn.commit()

    async def _create_user_from_row(self, row):
        return {
            'id': row[0],
            'name': row[1],
            'surname': row[2],
            'login': row[3],
            'password': row[4],
            'date_of_birth': str(row[5]),
            'permissions': row[6],
        }

    async def _set_password(self, data):
        if not data.get('password'):
            return
        data['password'] = sha256_crypt.using().hash(data['password'])

    async def _set_date_of_birth(self, data):
        if not data.get('date_of_birth'):
            return
        try:
            data['date_of_birth'] = date.fromisoformat(data['date_of_birth'])
        except ValueError:
            return True

    async def _set_permissions(self, data):
        if not data.get('permissions'):
            return
        perm = data['permissions']
        async with self.engine.connect() as conn:
            perm_id = await conn.scalar(
                sa.select(self.sub_model.c.id)
                .where(self.sub_model.c.perm_name == perm)
            )
        if not perm_id:
            return True
        data['permissions'] = perm_id

    async def _set_where(self, slug):
        if slug.isdigit():
            return self.model.c.id == int(slug)
        else:
            return self.model.c.login == slug
