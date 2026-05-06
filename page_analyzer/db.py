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
    cur.execute("SELECT id, name, created_at FROM urls ORDER BY id DESC")
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return urls


def get_url(url_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT id, name, created_at FROM urls WHERE id = %s",
        (url_id,)
    )
    url = cur.fetchone()
    cur.close()
    conn.close()
    return url


def get_url_by_name(name):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "SELECT id FROM urls WHERE name = %s",
        (name,)
    )
    url = cur.fetchone()
    cur.close()
    conn.close()
    return url


def add_url(url_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, NOW()) "
            "RETURNING id",
            (url_name,)
        )
        url_id = cur.fetchone()[0]
        conn.commit()
        return url_id
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.execute(
            "SELECT id FROM urls WHERE name = %s",
            (url_name,)
        )
        url_id = cur.fetchone()[0]
        return url_id
    finally:
        cur.close()
        conn.close()


def add_check(url_id, status_code, h1, title, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO checks (url_id, status_code, h1, title, description, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """,
        (url_id, status_code, h1, title, description)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_checks(url_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        """
        SELECT id, status_code, h1, title, description, created_at
        FROM checks
        WHERE url_id = %s
        ORDER BY id DESC
        """,
        (url_id,)
    )
    checks = cur.fetchall()
    cur.close()
    conn.close()
    return checks


def get_urls_with_checks():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('''
        SELECT
            u.id,
            u.name,
            u.created_at,
            c.created_at as last_check_date,
            c.status_code as last_check_status
        FROM urls u
        LEFT JOIN (
            SELECT DISTINCT ON (url_id) url_id, created_at, status_code
            FROM checks
            ORDER BY url_id, created_at DESC
        ) c ON u.id = c.url_id
        ORDER BY u.id DESC
    ''')
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return urls
