import sqlalchemy as sa

from passlib.hash import sha256_crypt
from datetime import date

from srv.store.pg import models


def setup_model_managers(app):
    app['model'] = {
        'user': User(),
    }


class User:
    """
    Managing user table operations.
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

        ret = await conn.execute(
            self.model.insert()
            .values(data)
            .returning(
                self.model.c.id,
                self.model.c.name,
                self.model.c.surname,
                self.model.c.login,
                self.model.c.password,
                sa.cast(self.model.c.date_of_birth, sa.String),
                self.model.c.permissions,
            )
        )
        row = ret.fetchone()
        if not row:
            return

        created_user = dict(row._mapping)
        await self._get_permissions(conn, created_user)
        return created_user

    async def read(self, conn, slug):
        where = await self._set_where(slug)
        ret = await conn.execute(
            sa.select(
                self.model.c.id,
                self.model.c.name,
                self.model.c.surname,
                self.model.c.login,
                self.model.c.password,
                sa.cast(self.model.c.date_of_birth, sa.String),
                self.sub_model.c.perm_name.label('permissions'),
            ).where(sa.and_(self.model.c.permissions == self.sub_model.c.id, where))
        )
        row = ret.fetchone()
        if row:
            return dict(row._mapping)

    async def read_all(self, conn):
        ret = await conn.execute(
            sa.select(
                self.model.c.id,
                self.model.c.name,
                self.model.c.surname,
                self.model.c.login,
                self.model.c.password,
                sa.cast(self.model.c.date_of_birth, sa.String),
                self.sub_model.c.perm_name.label('permissions'),
            ).where(self.model.c.permissions == self.sub_model.c.id)
        )
        return [dict(row._mapping) for row in ret]

    async def update(self, conn, slug, data):
        await self._set_password(data)
        await self._set_permissions(conn, data)

        where = await self._set_where(slug)
        ret = await conn.execute(
            self.model.update().values(data).where(where)
            .returning(
                self.model.c.id,
                self.model.c.name,
                self.model.c.surname,
                self.model.c.login,
                self.model.c.password,
                sa.cast(self.model.c.date_of_birth, sa.String),
                self.model.c.permissions,
            )
        )
        row = ret.fetchone()
        if not row:
            return

        updated_user = dict(row._mapping)
        await self._get_permissions(conn, updated_user)
        return updated_user

    async def delete(self, conn, slug):
        where = await self._set_where(slug)
        ret = await conn.execute(
            self.model.delete().where(where)
        )
        return ret.rowcount

    async def _set_password(self, data):
        """
        Password hashing.
        """
        if not data.get('password'):
            return
        data['password'] = sha256_crypt.using().hash(data['password'])

    async def _set_date_of_birth(self, data):
        """
        Date setting from iso format.
        """
        if not data.get('date_of_birth'):
            return
        data['date_of_birth'] = date.fromisoformat(data['date_of_birth'])

    async def _set_permissions(self, conn, user_data):
        """
        Setting permission id by permission name.
        """
        if not user_data.get('permissions'):
            return
        perm_name = user_data['permissions']
        perm_id = await conn.scalar(
            sa.select(self.sub_model.c.id)
            .where(self.sub_model.c.perm_name == perm_name)
        )
        user_data['permissions'] = perm_id

    async def _get_permissions(self, conn, user_data):
        """
        Setting permission name by permission id.
        """
        perm_id = user_data['permissions']
        perm_name = await conn.scalar(
            sa.select(self.sub_model.c.perm_name)
            .where(self.sub_model.c.id == perm_id)
        )
        user_data['permissions'] = perm_name

    async def _set_where(self, slug):
        """
        Setting 'sql: where' by id or login.
        """
        if slug.isdigit():
            return self.model.c.id == int(slug)
        else:
            return self.model.c.login == slug
