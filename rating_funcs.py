import sqlite3


def clean_db(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("delete from rating")
    cur.close()

def get_user_info(db_name, id, chat_id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    n = cur.execute("SELECT * FROM rating WHERE (userid = (?) and chat_id = (?))", (id, chat_id, )).fetchall()[0]
    cur.close()
    return n


def top_5_players(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    n = cur.execute("SELECT COUNT(*) FROM rating where score != '0'").fetchone()[0]
    users = cur.execute("select username, score from rating where score != '0' order by score desc limit 5").fetchall()
    for i in range(min(5, n) - len(users)):
        users.append(('', ''))
    cur.close()
    return users


def score_updates(db_name, id, score, username, chat_id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM rating WHERE (userid = (?) and chat_id = (?))", (id, chat_id, ))
    if cur.fetchone()[0] > 0:
        cur.execute("SELECT score FROM rating WHERE (userid = (?) and chat_id = (?))", (id, chat_id, ))
        cnt = cur.fetchone()[0] + score
        cur.execute("UPDATE rating SET score = (?) WHERE (userid = (?) and chat_id = (?))", (cnt, id, chat_id, ))
    else:
        cur.execute("INSERT INTO rating (userid, score, username, chat_id) VALUES (?, ?, ?, ?)", (id, score, username, chat_id))
    con.commit()
    cur.close()

