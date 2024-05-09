import sqlite3
from flask import g


def connect_db():
    sql = sqlite3.connect('users.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    # if g and 'sqlite_db' not in g:
    #     g.sqlite_db = connect_db()
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db