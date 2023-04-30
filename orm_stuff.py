from flask import Flask
from data import db_session
from data.chats import Chats, Rating

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
DB_NAME = 'data/crocodile.db'


def create_chat(c_id, s, w):
    db_session.global_init(DB_NAME)
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
        chat.players = ''
        db_sess.add(chat)
    else:
        chat.is_started = s
        chat.current_word = w
    db_sess.commit()

def create_rating(id, s, n, c_id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    user = Rating()
    user.user_id = id
    user.score = s
    user.username = n
    user.chat_id = c_id
    db_sess.add(user)
    db_sess.commit()


def score_updates(id, score, username, chat_id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    cnt = False
    for user in db_sess.query(Rating).filter(Rating.chat_id == chat_id).filter(Rating.user_id == id):
        user.score += score
        db_sess.commit()
        cnt = True
    if not cnt:
        create_rating(id, score, username, chat_id)

def change_started(id, s):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == id):
        chat.is_started = s
    db_sess.commit()


def change_ved(id, v):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == id):
        chat.ved = v
    db_sess.commit()


def change_word(id, w):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == id):
        chat.current_word = w
    db_sess.commit()

def get_user_info(id, c_id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    for user in db_sess.query(Rating).filter(Rating.chat_id == c_id).filter(Rating.user_id == id):
        return [user.user_id, user.score, user.username, user.chat_id]


def get_info(id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    try:
        for chat in db_sess.query(Chats).filter(Chats.id == id):
            return [chat.is_started, chat.ved, chat.current_word]
    except TypeError:
        return [False, '', '']

def top_5_players(c_id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    list_of_scores = []
    for user in db_sess.query(Rating).filter(Rating.chat_id == c_id):
        list_of_scores.append([user.username, user.score])
    return sorted(list_of_scores, key=lambda x: x[1], reverse=True)[0:5]

def get_user_score(id, c_id, u, s):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    cnt = False
    for user in db_sess.query(Rating).filter(Rating.chat_id == c_id).filter(Rating.user_id == id):
        score = user.score
        cnt = True
    if not cnt:
        create_rating(id, s, u, c_id)
        score = 0
    db_sess.commit()
    return score

def active_chat_players_add(c_id, user_id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == c_id):
        players = chat.players
        chat.players = ' '.join([players, str(user_id)])
    db_sess.commit()

def active_chat_players_remove(c_id, user_id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == c_id):
        players = chat.players
    chat.players = (players.replace(str(user_id), '')).strip()
    db_sess.commit()

def active_chat_players_clean(c_id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == c_id):
        chat.players = ''
    db_sess.commit()

def active_chat_players_get(c_id):
    db_session.global_init(DB_NAME)
    db_sess = db_session.create_session()
    for chat in db_sess.query(Chats).filter(Chats.id == c_id):
        return list(map(int, chat.players.split()))
