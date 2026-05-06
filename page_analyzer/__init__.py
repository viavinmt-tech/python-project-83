import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") # NOSONAR

    if not app.config["SECRET_KEY"] and os.getenv("FLASK_ENV") == "production":
        raise ValueError("SECRET_KEY must be set in production environment") # NOSONAR

    from page_analyzer import routes

    routes.init_app(app)

    return app


app = create_app()
__all__ = ["app"]
