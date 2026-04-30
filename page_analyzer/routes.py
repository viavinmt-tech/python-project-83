from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
import os

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    return conn

def init_app(app):
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/urls', methods=['POST'])
    def add_url():
        url = request.form.get('url')
        from urllib.parse import urlparse
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}"
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                (normalized, datetime.now())
            )
            url_id = cur.fetchone()[0]
            conn.commit()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('show_url', id=url_id))
        except psycopg2.IntegrityError:
            conn.rollback()
            cur.execute("SELECT id FROM urls WHERE name = %s", (normalized,))
            url_id = cur.fetchone()[0]
            flash('Страница уже существует', 'info')
            return redirect(url_for('show_url', id=url_id))
        finally:
            cur.close()
            conn.close()
    
    @app.route('/urls/<int:id>')
    def show_url(id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
        url = cur.fetchone()
        
        cur.execute("""
            SELECT * FROM url_checks 
            WHERE url_id = %s 
            ORDER BY created_at DESC
        """, (id,))
        checks = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not url:
            flash('Страница не найдена', 'error')
            return redirect(url_for('index'))
        
        return render_template('show_url.html', url=url, checks=checks)
    
    @app.route('/urls/<int:id>/checks', methods=['POST'])
    def check_url(id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO url_checks (url_id, created_at) VALUES (%s, %s)",
                (id, datetime.now())
            )
            conn.commit()
            flash('Страница успешно проверена', 'success')
        except Exception as e:
            flash('Произошла ошибка при проверке', 'danger')
            conn.rollback()
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('show_url', id=id))

    @app.route('/urls')
    def list_urls():
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT u.id, u.name, u.created_at, MAX(uc.created_at) as last_check_at
            FROM urls u
            LEFT JOIN url_checks uc ON u.id = uc.url_id
            GROUP BY u.id, u.name, u.created_at
            ORDER BY u.created_at DESC
        """)
        urls = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('urls.html', urls=urls)