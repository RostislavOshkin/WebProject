import sqlalchemy

from .db_session import SqlAlchemyBase


class File(SqlAlchemyBase):
    __tablename__ = 'files'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)