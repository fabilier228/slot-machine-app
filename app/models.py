from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    saldo = db.Column(db.Float(), nullable=False, default=0.0)
    games = db.relationship("GameLog")
    last_bonus_collected = db.Column(db.DateTime, default=None)


class GameLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    result = db.Column(db.Float(), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=db.func.now())