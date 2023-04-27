import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Config(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'configs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    person_id = sqlalchemy.Column(sqlalchemy.Integer)
    search = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=True)
