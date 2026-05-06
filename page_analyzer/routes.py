import requests
from bs4 import BeautifulSoup
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


def register_index_route(app):
    @app.route("/")
    def index():
        return render_template("index.html")


def register_add_url_route(app):
    @app.route("/urls", methods=["POST"])
    def add_url():
        url = request.form.get("url", "").strip()

        error = validate_url(url)
        if error:
            flash(error, "danger")
            return render_template("index.html"), 422

        normalized_url = normalize_url(url)
        existing_url = db.get_url_by_name(normalized_url)

        if existing_url:
            flash("Страница уже существует", "info")
            return redirect(url_for("show_url", id=existing_url["id"]))

        url_id = db.add_url(normalized_url)
        flash("Страница успешно добавлена", "success")
        return redirect(url_for("show_url", id=url_id))


def register_list_urls_route(app):
    @app.route("/urls")
    def list_urls():
        urls = db.get_urls_with_checks()
        return render_template("urls.html", urls=urls)


def register_show_url_route(app):
    @app.route("/urls/<int:id>")
    def show_url(id):
        url = db.get_url(id)
        if not url:
            flash("Страница не найдена", "danger")
            return redirect(url_for("index"))
        checks = db.get_checks(id)
        return render_template("url.html", url=url, checks=checks)


def register_run_check_route(app):
    @app.route("/urls/<int:id>/checks", methods=["POST"])
    def run_check(id):
        url_data = db.get_url(id)
        if not url_data:
            flash("Страница не найдена", "danger")
            return redirect(url_for("index"))

        try:
            response = requests.get(url_data["name"])
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            status_code = response.status_code
            h1 = soup.h1.string if soup.h1 else ""
            title = soup.title.string if soup.title else ""
            description = ""
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                description = meta_desc.get("content", "")

            db.add_check(id, status_code, h1, title, description)
            flash("Страница успешно проверена", "success")
        except requests.RequestException:
            flash("Произошла ошибка при проверке", "danger")

        return redirect(url_for("show_url", id=id))


def init_app(app):
    register_index_route(app)
    register_add_url_route(app)
    register_list_urls_route(app)
    register_show_url_route(app)
    register_run_check_route(app)
