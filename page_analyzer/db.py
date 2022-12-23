import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import errors
from datetime import datetime, date
import validators

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def add_url(name: str):
    """
    Function that inserts url into database,
    table: urls
    Keyword arguments:
        name : str - valid url for example 'https://www.example.com'
    """
    if not validators.url(name):
        return 'IncorrectUrl'

    UniqueViolation = errors.lookup('23505')
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO urls (name, created_at)
            VALUES (%(name)s, %(created_at)s)
            RETURNING id;
            """,
            {'name': name, 'created_at': datetime.now()})
        conn.commit()
        id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return id
    except UniqueViolation:
        cur.close()
        conn.close()
        return 'UniqueViolation'


def add_check(id: int):
    """
    Function that inserts url-check into database,
    table: url_checks
    Keyword arguments:
        id : int - id of url, referenses to urls (id)
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO url_checks (url_id, created_at)
        VALUES (%(id)s, %(created_at)s);
        """,
        {'id': id, 'created_at': datetime.now()})
    conn.commit()
    cur.close()
    conn.close()


def get_urls() -> list:
    """
    Function that returns urls from database,
    table: urls
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM urls;")
    output = cur.fetchall()
    cur.close()
    conn.close()
    return output


def get_checks(id) -> list:
    """
    Function that returns checks by url from database,
    table: url_checks
    Keyword arguments:
        id : int - id of url
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM url_checks
        WHERE url_id = %(id)s;""",
        {'id': id})
    result = cur.fetchall()
    cur.close()
    conn.close()
    output = list([item[:-1] + (ts_to_date(item[-1]),) for item in result])
    return output


def find_url_by_id(id: int) -> dict:
    """
    Function that returns row from database by id
    Keyword arguments:
        id : int - id of row
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM urls
        WHERE id = %(id)s;""",
        {'id': id})
    row = cur.fetchone()
    id, name, created_at = row
    created_at = created_at.timestamp()
    cur.close()
    conn.close()
    return {
        'id': id,
        'name': name,
        'created_at': date.fromtimestamp(created_at)
        }


def find_url_by_name(name: str) -> dict:
    """
    Function that returns row from database by name
    Keyword arguments:
        name : str - name of url in a row
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM urls
        WHERE name = %(name)s;""",
        {'name': name})
    row = cur.fetchone()
    id, name, created_at = row
    cur.close()
    conn.close()
    return {
        'id': id,
        'name': name,
        'created_at': ts_to_date(created_at)
        }


def ts_to_date(ts):
    return date.fromtimestamp(ts.timestamp())
