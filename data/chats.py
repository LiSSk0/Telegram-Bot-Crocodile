import sqlalchemy
from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase):
    __tablename__ = 'chats'
    i = sqlalchemy.Column(sqlalchemy.Integer,
                          primary_key=True, autoincrement=True)

    id = sqlalchemy.Column(sqlalchemy.Integer)
    ved = sqlalchemy.Column(sqlalchemy.Integer)
    is_started = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    current_word = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    players = sqlalchemy.Column(sqlalchemy.String)


class Rating(SqlAlchemyBase):
    __tablename__ = 'rating'
    i = sqlalchemy.Column(sqlalchemy.Integer,
                                primary_key=True, autoincrement=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    score = sqlalchemy.Column(sqlalchemy.Integer)
    username = sqlalchemy.Column(sqlalchemy.String)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer)
