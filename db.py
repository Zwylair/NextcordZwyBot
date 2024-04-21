import sqlite3
import settings


def get_conn():
    return sqlite3.connect(settings.SQL_DB_PATH)


def get_cursor():
    return get_conn().cursor()
