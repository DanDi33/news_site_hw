from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from connect_db import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"<users {self.id}>"

    def set_password(self, password):
        self.psw = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.psw, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(50))
    post = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<posts {self.id}>"
