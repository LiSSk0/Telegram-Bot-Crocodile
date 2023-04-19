import sqlite3


def clean_db(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("delete from rating")
    cur.close()


def top_5_players(db_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    n = cur.execute("SELECT COUNT(*) FROM rating where score != '0'").fetchone()[0]
    users = cur.execute("select username, score from rating where score != '0' order by score desc limit 5").fetchall()
    for i in range(min(5, n) - len(users)):
        users.append(('', ''))
    cur.close()
    return users


def score_updates(db_name, id, score, username):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM rating WHERE userid = (?)", (id,))
    if cur.fetchone()[0] > 0:
        cur.execute("SELECT score FROM rating WHERE userid = (?)", (id,))
        cnt = cur.fetchone()[0] + score
        cur.execute("UPDATE rating SET score = (?) WHERE userid = (?)", (cnt, id,))
    else:
        cur.execute("INSERT INTO rating (userid, score, username) VALUES (?, ?, ?)", (id, score, username))
    con.commit()
    cur.close()