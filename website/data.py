from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Product {self.label}>'



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(200))
    products = db.relationship('Product', backref='user', lazy=True) 

    def __repr__(self):
        return f'<User {self.name}>'

