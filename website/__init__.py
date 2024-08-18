from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
from flask_pymongo import PyMongo

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']  =  os.getenv('SECRET_KEY', 'default_key_if_not_set')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .auth import auth
    from .pages import pages

    app.register_blueprint(pages, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .data import User

    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    
    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')


