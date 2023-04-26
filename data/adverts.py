import datetime
import re
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Advert(SqlAlchemyBase):
    __tablename__ = 'adverts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    id_person = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    description = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.String, default='Договорная')
    data = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    id_files = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("files.id"), autoincrement=True)
    for_search = sqlalchemy.Column(sqlalchemy.String)

    user = orm.relationship('User')
    files = orm.relationship("File")
