import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    SQLALCHEMY_ECHO = False


class Production(Config):
    SQLALCHEMY_ECHO = True

class Development(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'postgres://badrikueugene:me55edup@localhost:5432/dev_bucketlist'


class Testing(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'tests/test.sqlite3')
    SQLALCHEMY_ECHO = True
