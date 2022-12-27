import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime, date

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def ts_to_date(ts):
    """
    Converting timestamp into date (YYYY-MM-DD)
    """
    return date.fromtimestamp(ts.timestamp())


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
    if exist_url(name)[0]:
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
        with conn.cursor() as cur:
            cur.execute(
                """SELECT u.id, u.name, ch.created_at, ch.status_code
                FROM urls as u
                LEFT JOIN url_checks AS ch
                ON u.id = ch.url_id
                AND ch.created_at =
                    (SELECT MAX(created_at) FROM url_checks
                    WHERE url_id = u.id)
                ORDER BY u.id;""")
            rows = cur.fetchall()
    conn.close()
    urls = []
    for row in rows:
        url = {}
        url.update({'id': row[0]})
        url.update({'name': row[1]})
        url.update(
            {'date': ts_to_date(row[2])}
        ) if row[2] is not None else url.setdefault('date', '')
        url.update(
            {'status': row[3]}
        ) if row[3] is not None else url.setdefault('status', '')
        urls.append(url)
    return urls


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
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM url_checks
                WHERE url_id = %(id)s
                ORDER BY id;""",
                {'id': id})
            rows = cur.fetchall()
    conn.close()
    checks = []
    for row in rows:
        check = {}
        check.update({'id': row[0]})
        check.update({'status': row[2]})
        check.update(
            {'h1': row[3]}
        ) if row[3] is not None else check.setdefault('h1', '')
        check.update(
            {'title': row[4]}
        ) if row[4] is not None else check.setdefault('title', '')
        check.update(
            {'content': row[5]}
        ) if row[5] is not None else check.setdefault('content', '')
        check.update({'date': ts_to_date(row[6])})
        checks.append(check)
    return checks


def find_url(id: int) -> dict:
    """
    Function that returns row in a dict from database by id.
    Keyword arguments:
        id : int - id of row
    Tables:
        urls
    Statements:
        SELECT
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM urls
                WHERE id = %(id)s;""",
                {'id': id})
            row = cur.fetchone()
    conn.close()
    id, name, created_at = row
    return {
        'id': id,
        'name': name,
        'created_at': ts_to_date(created_at)
    }


def exist_url(value: str) -> tuple:
    """
    Returns tuple (bool, id or None)
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id FROM urls
                WHERE name = %(value)s;""",
                {'value': value})
            id = cur.fetchone()
    conn.close()
    if id is None:
        return (False, id)
    return (True, id[0])
