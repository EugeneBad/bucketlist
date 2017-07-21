import hashlib
import jwt

import datetime

from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.db.models import Bucketlist, Item, User
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

    def set_password(self, password):
        """
        Method that salts a password string using the SECRET_KEY;
        to return a sha256 hashed string.
        """

        salted_password = password + SECRET_KEY

        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
        return hashed_password

class Register(Request, Resource):
    """ View class called to register a new user, accessible only via a POST request  """
    def post(self):
        login_data = self.parse_args()

        # Both username and password have to be supplied
        if not login_data.get('username') or not login_data.get('password'):
            return 'Username and password needed', 400

        duplicate_user = User.query.filter_by(username=login_data.get('username')).first()

        # Username must be unique
        if duplicate_user:
            return 'Username already exists', 409

        # Passwords should not be stored in their raw string form but rather hashed.
        secure_password = self.set_password(password=login_data.get('password'))

        new_user = User(username=login_data.get('username'),
                        password=secure_password)
        session.add(new_user)
        session.commit()

        # Token payload is encoded with the new user's username and an expiry period.
        payload = {'username': new_user.username,
                   "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=600)}
        auth_token = jwt.encode(payload, key=SECRET_KEY).decode()

        return {'auth_token': auth_token}, 200

