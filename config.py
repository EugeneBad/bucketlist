import os


class Config:
    SECRET_KEY = os.urandom(50)
    DEBUG = False
    SQLALCHEMY_ECHO = False


class Production(Config):
    SQLALCHEMY_ECHO = True
    # SQLALCHEMY_DATABASE_URI


class Development(Config):
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'postgres://badrikueugene:me55edup@localhost:5432/dev_bucketlist'


class Testing(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../app/test_db.sqlite3'
    SQLALCHEMY_ECHO = True
