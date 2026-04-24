import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    from page_analyzer import routes
    routes.init_app(app)
    
    return app

app = create_app()
__all__ = ['app']
