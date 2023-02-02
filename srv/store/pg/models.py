from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, String, Date


metadata = MetaData()


user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(32)),
    Column('surname', String(32)),
    Column('login', String(128), unique=True, nullable=False),
    Column('password', String(256), nullable=False),
    Column('date_of_birth', Date),
    Column('permissions', ForeignKey('permissions.id', ondelete='SET NULL'), default=3),
)


permissions = Table(
    'permissions',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('perm_name', String(10), nullable=False),
)


