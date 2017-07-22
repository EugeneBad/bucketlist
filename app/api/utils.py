import datetime
import hashlib
from flask_restful.reqparse import RequestParser
import jwt
from app.app import session, SECRET_KEY
from app.db.models import User


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

    def is_authenticated(self):
        """
        Method used to identify the user of an incoming request via the token;
        returns True if user is valid.
        """
        try:
            token = self.parse_args()['token']
            user_data = jwt.decode(token, key=SECRET_KEY)
            self.current_user = session.query(User).filter_by(username=user_data['username']).first()
            return True

        except (AttributeError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False

    def generate_token(self, username):
        # Token payload is encoded with the new user's username and an expiry period.
        payload = {'username': username,
                   "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=600)}

        auth_token = jwt.encode(payload, key=SECRET_KEY).decode()
        return auth_token

    def save(self, obj):
        session.add(obj)
        session.commit()

    def remove(self, obj):
        session.delete(obj)
        session.commit()

    def paginated(self, obj_list):
        """ Method used to paginate results in an object list """
        self.page = 1 if not self.parse_args().get('page', 1) else int(self.parse_args().get('page'))
        self.limit = 20 if not self.parse_args().get('limit', 20) else int(self.parse_args().get('limit'))

        paginator_obj = obj_list.paginate(1, self.limit)
        self.total_pages = paginator_obj.pages

        # If the requested page number is out of bounds, return the last page.
        if self.page > self.total_pages:
            self.page = self.total_pages

        paginated_list = obj_list.paginate(self.page, self.limit)
        return paginated_list.items
