import sqlalchemy as sa

from passlib.hash import sha256_crypt
from datetime import date

from . import models


class User:
    model = models.user
    sub_model = models.permissions

    async def create(self, conn, data):
        await self._set_password(data)
        await self._set_date_of_birth(data)
        await self._set_permissions(conn, data)

        ret = await conn.execute(
            self.model.insert(), data
        )
        return ret.rowcount

    async def read(self, conn, slug):
        where = await self._set_where(slug)
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
            return await self._create_json_from_row(row)

    async def read_all(self, conn):
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
        return [await self._create_json_from_row(row) for row in ret]

    async def update(self, conn, slug, data):
        await self._set_password(data)
        await self._set_date_of_birth(data)
        await self._set_permissions(conn, data)

        where = await self._set_where(slug)
        ret = await conn.execute(
            self.model.update().values(data).where(where)
        )
        return ret.rowcount

    async def delete(self, conn, slug):
        where = await self._set_where(slug)
        ret = await conn.execute(
            self.model.delete().where(where)
        )
        return ret.rowcount

    async def _create_json_from_row(self, row):
        user = dict(row)
        user['date_of_birth'] = str(user['date_of_birth'])
        user['permissions'] = user['perm_name']
        user.pop('perm_name')
        return user

    async def _set_password(self, data):
        if not data.get('password'):
            return
        data['password'] = sha256_crypt.using().hash(data['password'])

    async def _set_date_of_birth(self, data):
        if not data.get('date_of_birth'):
            return
        data['date_of_birth'] = date.fromisoformat(data['date_of_birth'])

    async def _set_permissions(self, conn, data):
        if not data.get('permissions'):
            return

        perm = data['permissions']
        perm_id = await conn.scalar(
            sa.select(self.sub_model.c.id)
            .where(self.sub_model.c.perm_name == perm)
        )
        if not perm_id:
            raise ValueError

        data['permissions'] = perm_id

    async def _set_where(self, slug):
        if slug.isdigit():
            return self.model.c.id == int(slug)
        else:
            return self.model.c.login == slug
