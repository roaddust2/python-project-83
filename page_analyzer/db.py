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
    Function that adds url into database
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
    
    


def get_urls() -> list:
    """
    Function that returns urls from database
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM urls;")
    output = cur.fetchall()
    cur.close()
    conn.close()
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


def find_url_by_name(name: int) -> dict:
    """
    Function that returns row from database by id
    Keyword arguments:
        id : int - id of row
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM urls
        WHERE name = %(name)s;""",
        {'name': name})
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
