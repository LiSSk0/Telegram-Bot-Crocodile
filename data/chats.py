import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    ved = sqlalchemy.Column(sqlalchemy.Integer)
    is_started = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    current_word = sqlalchemy.Column(sqlalchemy.String, nullable=False)