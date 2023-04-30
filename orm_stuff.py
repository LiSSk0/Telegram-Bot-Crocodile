from flask import Flask
from data import db_session
from data.chats import Chats

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def create_chat(c_id, s, w):
    db_session.global_init("db/croc.db")
    db_sess = db_session.create_session()
    cnt = 0
    for chat in db_sess.query(Chats).filter(Chats.id == c_id):
        cnt += 1
    if cnt == 0:
        chat = Chats()
        chat.id = c_id
        chat.ved = ''
        chat.is_started = s
        chat.current_word = w
        db_sess.add(chat)
    else:
        chat.is_started = s
        chat.current_word = w
    db_sess.commit()


def change_started(id, s):
    db_session.global_init("db/croc.db")
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == id):
        chat.is_started = s
    db_sess.commit()


def change_ved(id, v):
    db_session.global_init("db/croc.db")
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == id):
        chat.ved = v
    db_sess.commit()


def change_word(id, w):
    db_session.global_init("db/croc.db")
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == id):
        chat.current_word = w
    db_sess.commit()


def get_info(id):
    db_session.global_init("db/croc.db")
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == id):
        return [chat.is_started, chat.ved, chat.current_word]

