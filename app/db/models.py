from app.app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class Bucketlist(db.Model):
    __tablename__ = 'bucketlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    cd = db.Column(db.Date)
    md = db.Column(db.Date)
    cb = db.Column(db.String(35))
    items = db.relationship('Item', backref='bucketlist')


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    cd = db.Column(db.Date)
    md = db.Column(db.Date)
    completed = db.Column(db.Boolean)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlist.id'))

db.create_all()
