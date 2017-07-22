from datetime import datetime
from app.app import db


class Bucketlist(db.Model):
    __tablename__ = 'bucketlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    creation_date = db.Column(db.Date,
                              default=datetime.now().date(),
                              nullable=False)
    modification_date = db.Column(db.Date,
                                  default=datetime.now().date(),
                                  onupdate=datetime.now().date(),
                                  nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', backref='bucketlists')
    items = db.relationship('Item', backref='bucketlist')


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),
                     unique=True,
                     nullable=False)
    creation_date = db.Column(db.Date, default=datetime.now().date())
    modification_date = db.Column(db.Date,
                                  default=datetime.now().date(),
                                  onupdate=datetime.now().date())
    completed = db.Column(db.Boolean, default=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlist.id'))


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


