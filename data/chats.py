import sqlalchemy
from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    ved = sqlalchemy.Column(sqlalchemy.Integer)
    is_started = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    current_word = sqlalchemy.Column(sqlalchemy.String, nullable=False)

class Rating(SqlAlchemyBase):
    __tablename__ = 'rating'

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    score = sqlalchemy.Column(sqlalchemy.Integer)
    username = sqlalchemy.Column(sqlalchemy.String)
    chat_id = sqlalchemy.Column(sqlalchemy.String)