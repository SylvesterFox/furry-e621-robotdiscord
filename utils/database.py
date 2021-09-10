import psycopg2
import psycopg2.extras
import os

from utils.bot import settings_app

def connect_data():
    settings = settings_app()
    if settings['heroku_mod']:
        host = os.environ['host_base']
        database = os.environ['database']
        user = os.environ['user_base']
        password = os.environ['password']
        return [host, database, user, password]
    else:
        host = "localhost"
        database = "e621tags"
        user = "postgres"
        password = "0000"
        return [host, database, user, password]

def db_conn(func):
    data_conn = connect_data()
    def inner(*args, **kwargs):
        con = psycopg2.connect(
        host = data_conn[0],
        database=data_conn[1],
        user=data_conn[2],
        password=data_conn[3])
        res = func(*args, con=con, **kwargs)
        return res
    return inner


@db_conn
def create_table(con):
    try:
        cur = con.cursor()
        cur.execute("CREATE TABLE tag (id SERIAL PRIMARY KEY, guild_id BIGINT NOT NULL, channel_id BIGINT NOT NULL, tag VARCHAR NOT NULL, activate BOOL NOT NULL, user_id BIGINT NOT NULL, id_tag BIGINT NOT NULL);")
        con.commit()
        con.close()
    except Exception as e:
        con.close()

@db_conn
def insert_data(con, guild_id: int, channel_id: int, tag: str, activate: bool, user: int, id_tag: int=0):
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO tag (guild_id, channel_id, tag, activate, user_id, id_tag) VALUES (%s, %s, %s, %s, %s, %s)", (guild_id, channel_id, tag, activate, user, id_tag))
        con.commit()
        con.close()
    except Exception as e:
        con.close()
        print(e)

@db_conn
def get_tags_server(con, guild_id: int, user_id: int):
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM tag WHERE user_id = %s AND guild_id = %s", (user_id, guild_id))
    res = cur.fetchall()
    con.close()
    return res

@db_conn
def delete_tag(con, user_id: int, id: int):
    cur = con.cursor()
    cur.execute("DELETE FROM tag WHERE id = %s AND user_id = %s", (id, user_id))
    con.commit()
    con.close()

@db_conn
def get_all(con):
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT channel_id, tag, activate, id, id_tag FROM tag")
    res = cur.fetchall()
    con.close()
    return res

@db_conn
def update_post_id(con, id: int, post_id: id):
    cur = con.cursor()
    cur.execute("UPDATE tag SET id_tag = %s WHERE id = %s", (post_id, id))
    con.commit()
    con.close()


@db_conn
def update_activate(con, id: int, switch: bool):
    cur = con.cursor()
    cur.execute("UPDATE tag SET activate = %s WHERE id = %s", (switch, id))
    con.commit()
    con.close()

@db_conn
def get_activate(con, id: int):
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT activate, id, tag, channel_id FROM tag WHERE id = %s", (id, ))
    res = cur.fetchall()
    con.close()
    return res
