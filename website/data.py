import enum
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Enum as SqlEnum



class UserStatusEnum(enum.Enum):
    ORDER_RECEIVED = "order received"
    ORDER_PREPARING = "order preparing"
    ORDER_MADE = "order made"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150))
    status = db.Column(SqlEnum(UserStatusEnum), default=UserStatusEnum.ORDER_PREPARING, nullable=False)
    price = db.Column(db.Float)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(200))
    products = db.relationship('Product', backref='user', lazy=True)


