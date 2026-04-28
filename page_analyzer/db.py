import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    DATABASE_URL = os.getenv('DATABASE_URL')
    return psycopg2.connect(DATABASE_URL)


def get_urls():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT id, name, created_at FROM urls ORDER BY id DESC')
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return urls


def get_url(url_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT id, name, created_at FROM urls WHERE id = %s', (url_id,))
    url = cur.fetchone()
    cur.close()
    conn.close()
    return url


def add_url(url_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, NOW()) RETURNING id',
            (url_name,)
        )
        url_id = cur.fetchone()[0]
        conn.commit()
        return url_id
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.execute('SELECT id FROM urls WHERE name = %s', (url_name,))
        url_id = cur.fetchone()[0]
        return url_id
    finally:
        cur.close()
        conn.close()
