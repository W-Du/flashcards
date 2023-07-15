from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import ForeignKey

list_user = db.Table(
    'list_user',
    db.Column('list_id', db.Integer, db.ForeignKey('lists.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

word_list = db.Table(
    'word_list',
    db.Column('word_id', db.Integer, db.ForeignKey('words.id')),
    db.Column('list_id', db.Integer, db.ForeignKey('lists.id')),
)

word_user = db.Table(
    'word_user',
    db.Column('word_id', db.Integer, db.ForeignKey('words.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), index = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    daily_goal = db.Column(db.Integer, nullable=True)
    lists = db.relationship('List', secondary=list_user, back_populates='users', cascade='all, delete')
    words = db.relationship('Word', secondary=word_user, back_populates='users', cascade='all, delete')

    def set_password(self, passwordInput):
        self.password_hash = generate_password_hash(passwordInput)
    
    def check_password(self, passwordInput):
        return check_password_hash(self.password_hash, passwordInput)


class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key = True)
    listname = db.Column(db.String(30), index = True)
    words = db.relationship('Word', secondary=word_list, back_populates='lists', cascade='save-update, merge')
    users = db.relationship('User', secondary=list_user, back_populates='lists', cascade='save-update, merge')

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(30), index=True, unique=False)
    description = db.Column(db.String)
    priority = db.Column(db.Integer, default=3, nullable=False)
    lists = db.relationship('List', secondary=word_list, back_populates='words', cascade='save-update, merge')
    users = db.relationship('User', secondary=word_user, back_populates='words', cascade='save-update, merge')
    