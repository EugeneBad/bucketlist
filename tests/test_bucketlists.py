from flask_restful.reqparse import RequestParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app import app

db_engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))
session = sessionmaker(bind=db_engine)()
SECRET_KEY = app.config.get('SECRET_KEY')


class Request(RequestParser):
    def __init__(self):
        """
        Utility class used for performing generic manipulations on incoming request objects.
        Initialised with all the arguments to be used by the view classes.

        """
        super().__init__()
        self.add_argument('name', location='form')
        self.add_argument('done', location='form')
        self.add_argument('username', location='form')
        self.add_argument('password', location='form')
        self.add_argument('token', location='headers')
        self.add_argument('page', location='args')
        self.add_argument('limit', location='args')
