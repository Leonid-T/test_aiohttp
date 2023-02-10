import sqlalchemy as sa
from passlib.hash import sha256_crypt

from srv.store.pg import models


def setup_model_managers(app):
    app['model'] = {
        'user': UserManager(),
    }


class UserManager:
    """
    Managing user table operations
    """
    _model = models.user
    _sub_model = models.permissions

    @property
    def model(self):
        return self._model

    @property
    def sub_model(self):
        return self._sub_model

    async def create(self, conn, data):
        await self._set_password(data)
        await self._set_permissions(conn, data)

        user_id = await conn.scalar(
            self.model.insert().values(data).returning(self.model.c.id)
        )
        if user_id:
            return await self._get_user_by_where(conn, self.model.c.id == user_id)

    async def read(self, conn, slug):
        where = await self._set_where(slug)
        return await self._get_user_by_where(conn, where)

    async def read_all(self, conn):
        ret = await conn.execute(
            sa.select(
                self.model.c.id,
                self.model.c.name,
                self.model.c.surname,
                self.model.c.login,
                self.model.c.password,
                self.model.c.date_of_birth,
                self.sub_model.c.perm_name.label('permissions'),
            ).where(self.model.c.permissions == self.sub_model.c.id)
        )
        return ret.fetchall()

    async def update(self, conn, slug, data):
        await self._set_password(data)
        await self._set_permissions(conn, data)

        where = await self._set_where(slug)
        user_id = await conn.scalar(
            self.model.update().values(data).where(where).returning(self.model.c.id)
        )
        if user_id:
            return await self._get_user_by_where(conn, self.model.c.id == user_id)

    async def delete(self, conn, slug):
        where = await self._set_where(slug)
        ret = await conn.execute(
            self.model.delete().where(where)
        )
        return ret.rowcount

    async def _set_password(self, data):
        """
        Password hashing
        """
        if not data.get('password'):
            return
        data['password'] = sha256_crypt.using().hash(data['password'])

    async def _set_permissions(self, conn, user_data):
        """
        Setting permission id by permission name
        """
        if not user_data.get('permissions'):
            return
        perm_name = user_data['permissions']
        perm_id = await conn.scalar(
            sa.select(self.sub_model.c.id)
            .where(self.sub_model.c.perm_name == perm_name)
        )
        user_data['permissions'] = perm_id

    async def _get_user_by_where(self, conn, where):
        """
        Returns the row view of the user using the where query parameter
        """
        ret = await conn.execute(
            sa.select(
                self.model.c.id,
                self.model.c.name,
                self.model.c.surname,
                self.model.c.login,
                self.model.c.password,
                self.model.c.date_of_birth,
                self.sub_model.c.perm_name.label('permissions'),
            ).where(sa.and_(self.model.c.permissions == self.sub_model.c.id, where))
        )
        row = ret.fetchone()
        return row

    async def _set_where(self, slug):
        """
        Setting 'sql: where' by id or login
        """
        if slug.isdigit():
            return self.model.c.id == int(slug)
        else:
            return self.model.c.login == slug
