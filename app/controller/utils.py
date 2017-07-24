import datetime
import hashlib
from flask_restful.reqparse import RequestParser
import jwt
from app import session, SECRET_KEY
from app.database.models import User
from functools import wraps


class RequestMixin(RequestParser):
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
        self.add_argument('offset', location='args')
        self.add_argument('limit', location='args')
        self.add_argument('q', location='args')

    def set_password(self, password):
        """
        Method that salts a password string using the SECRET_KEY;
        to return a sha256 hashed string.
        """

        salted_password = password + SECRET_KEY

        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
        return hashed_password

    @staticmethod
    def is_authenticated(view_method):
        """
        Decorator method used to identify the user of an incoming request via the token.
        Returns a 401 if:- Token is not supplied
                         - Token is invalid
                         - Token is expired
        """
        @wraps(view_method)
        def view_wrapper(self, **kwargs):
            try:

                token = self.parse_args()['token']
                user_data = jwt.decode(token, key=SECRET_KEY)
                self.current_user = session.query(User).filter_by(username=user_data['username']).first()
                return view_method(self, **kwargs)

            except (AttributeError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return 'Please login', 401
        return view_wrapper

    def generate_token(self, username):
        """
        Method that takes a username as argument and encodes a token;
        using the username in the payload
        """
        # Token payload is encoded with the new user's username and an expiry period.
        payload = {'username': username,
                   "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=600)}

        auth_token = jwt.encode(payload, key=SECRET_KEY).decode()
        return auth_token

    def save(self, obj):
        """ Save an object to the database """

        session.add(obj)
        session.commit()

    def remove(self, obj):
        """ Remove an object from the database """

        session.delete(obj)
        session.commit()

    def paginated(self, obj_list):
        """ Method used to paginate results in an object list """
        self.page = 1 if not self.parse_args().get('offset') else int(self.parse_args().get('offset'))
        self.limit = 20 if not self.parse_args().get('limit') else int(self.parse_args().get('limit'))

        paginator_obj = obj_list.paginate(1, self.limit)
        self.total_pages = paginator_obj.pages

        # If the requested page number is out of bounds, return the last page.
        if self.page > self.total_pages:
            self.page = self.total_pages

        paginated_list = obj_list.paginate(self.page, self.limit)
        return paginated_list.items
