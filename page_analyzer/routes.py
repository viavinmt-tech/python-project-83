import validators
from urllib.parse import urlparse
from flask import render_template, request, redirect, url_for, flash
from page_analyzer import db


def normalize_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def validate_url(url):
    if not url:
        return "URL обязателен"
    if len(url) > 255:
        return "URL превышает 255 символов"
    if not validators.url(url):
        return "Некорректный URL"
    return None


def init_app(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/urls', methods=['POST'])
    def add_url():
        url = request.form.get('url', '').strip()
        
        # Валидация
        error = validate_url(url)
        if error:
            flash(error, 'danger')
            return render_template('index.html'), 422
        
        # Нормализация URL
        normalized_url = normalize_url(url)
        
        # Добавление в базу данных
        url_id = db.add_url(normalized_url)
        
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('show_url', id=url_id))

    @app.route('/urls')
    def list_urls():
        urls = db.get_urls()
        return render_template('urls.html', urls=urls)

    @app.route('/urls/<int:id>')
    def show_url(id):
        url = db.get_url(id)
        if not url:
            flash('Страница не найдена', 'danger')
            return redirect(url_for('index'))
        return render_template('url.html', url=url)
