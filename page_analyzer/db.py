import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def add_url(name: str):
    """
    Function that inserts url into database.
    On success returns row id, else returns None
    Keyword arguments:
        name : str - valid url for example 'https://www.example.com'
    Tables:
        urls
    Statements:
        INSERT INTO RETURNING
    """
    if exist_url(name):
        return None
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO urls (name, created_at)
                    VALUES (%(name)s, %(created_at)s)
                    RETURNING id;
                    """,
                    {'name': name, 'created_at': datetime.now()})
                id = cur.fetchone()[0]
                return id
    except psycopg2.Error:
        return None
    finally:
        conn.close()


def add_check(check: dict):
    """
    Function that inserts url-check into database.
    On success returns row id, else returns None
    Keyword arguments:
        check : dict - url-check details in dict type
    Tables:
        url_checks
    Statements:
        INSERT INTO RETURNING
    """
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO url_checks (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        created_at)
                    VALUES (
                        %(id)s,
                        %(status_code)s,
                        %(h1)s,
                        %(title)s,
                        %(content)s,
                        %(created_at)s)
                    RETURNING id;""", {
                        'id': check['id'],
                        'status_code': check['status_code'],
                        'h1': check['h1'],
                        'title': check['title'],
                        'content': str(check['content']),
                        'created_at': datetime.now()}
                )
                id = cur.fetchone()[0]
                return id
    except psycopg2.Error:
        return None
    finally:
        conn.close()


def get_urls() -> list:
    """
    Function that returns urls from database in a list with dicts.
    Tables:
        urls, url_checks
    Statements:
        SELECT, LEFT JOIN
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                """SELECT
                    u.id,
                    u.name,
                    COALESCE(
                        CAST(
                            DATE(ch.created_at) AS varchar), '') as created_at,
                    COALESCE(ch.status_code, '') as status_code
                FROM urls as u
                LEFT JOIN url_checks AS ch
                ON u.id = ch.url_id
                AND ch.created_at =
                    (SELECT MAX(created_at) FROM url_checks
                    WHERE url_id = u.id)
                ORDER BY u.id;""")
            rows = cur.fetchall()
    conn.close()
    return rows


def get_checks(id: int) -> list:
    """
    Function that returns checks by url from database in a list with dicts.
    Keyword arguments:
        id : int - id of url
    Tables:
        url_checks
    Statements:
        SELECT
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                """SELECT
                id,
                status_code,
                COALESCE(h1, '') as h1,
                COALESCE(title, '') as title,
                COALESCE(description, '') as content,
                DATE(created_at) as created_at
                 FROM url_checks
                WHERE url_id = %s
                ORDER BY id;""", (id,))
            rows = cur.fetchall()
    conn.close()
    return rows


def find_url(value) -> dict:
    """
    Function that returns row from database
    Keyword arguments:
        value - id or name of url
    Tables:
        urls
    Statements:
        SELECT
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            match value:
                case int():
                    cur.execute(
                        """SELECT id, name, DATE(created_at) as created_at
                        FROM urls
                        WHERE id = %s;""", (value,))
                    row = cur.fetchone()
                case str():
                    cur.execute(
                        """SELECT id, name, DATE(created_at) as created_at
                        FROM urls
                        WHERE name = %s;""", (value,))
                    row = cur.fetchone()
    conn.close()
    return row


def exist_url(name: str) -> bool:
    """
    Returns True if exists, False if not
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM urls WHERE name = %s;", (name,))
            result = cur.fetchone()
    conn.close()
    return bool(result[0])
