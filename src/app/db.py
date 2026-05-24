from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error

from app.config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def test_connection():
    try:
        conn = get_connection()
        conn.close()
        return True, None
    except Error as exc:
        return False, str(exc)


@contextmanager
def db_cursor(dictionary=True):
    conn = get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        conn.commit()
    except Error:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
