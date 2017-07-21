import hashlib
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import datetime

from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.db.models import Bucketlist, Item, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
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

        except (AttributeError, ExpiredSignatureError, InvalidTokenError):
            return False

    def paginated(self, obj_list):
        """ Method used to paginate results in an object list """
        self.page = 1 if not self.parse_args().get('page') else int(self.parse_args().get('page'))
        self.limit = 20 if not self.parse_args().get('limit') else int(self.parse_args().get('limit'))

        paginator_obj = obj_list.paginate(1, self.limit)
        self.total_pages = paginator_obj.pages

        # If the requested page number is out of bounds, return the last page.
        if self.page > self.total_pages:
            self.page = self.total_pages

        paginated_list = obj_list.paginate(self.page, self.limit)
        return paginated_list.items


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


class Login(Request, Resource):
    """ Class based view used to log in a user, accessible only via a POST request """
    def post(self):
        login_data = self.parse_args()

        # Both username and password have to be supplied
        if not login_data.get('username') or not login_data.get('password'):
            return 'Both username and password required', 400

        user = User.query.filter_by(username=login_data.get('username')).first()

        # User has to exist and password supplied has to be correct.
        if not user or self.set_password(login_data.get('password')) != user.password:
            return 'Check username and password', 400

        # Token payload is encoded with username and expiry date
        payload = {'username': user.username,
                   "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=600)}
        auth_token = jwt.encode(payload, key=SECRET_KEY).decode()

        return {'auth_token': auth_token}, 200


class Bucketlists(Request, Resource):
    """
    Class based view that handles: display of bucketlists using the GET http verb
    and creation of bucketlists using the POST http verb
    """
    def get(self):
        """ Called for a GET request """
        # View is only accessible by a logged in user.
        if not self.is_authenticated():
            return 'Please login', 401

        bucketlists = Bucketlist.query.filter_by(created_by=self.current_user)

        if not len(list(bucketlists)):
            return {'Bucketlists': 'None'}, 200

        paginated_list = self.paginated(bucketlists)

        # List comprehension that generates individual dictionaries of bucketlists
        list_of_bucketlists = [{'id': bucketlist.id,
                                'name': bucketlist.name,
                                'items': 'None' if not bucketlist.items else len(bucketlist.items),
                                'date_created': str(bucketlist.creation_date),
                                'created_by': self.current_user.username} for bucketlist in paginated_list]
        return {'Bucketlists': list_of_bucketlists,
                'Page': '{} of {}'.format(self.page, self.total_pages)}, 200

    def post(self):
        """ Called for a POST request """
        if not self.is_authenticated():
            return 'Please login', 401

        request_args = self.parse_args()

        if not request_args.get('name'):
            return 'Bucketlist name needed', 400

        try:
            new_bucketlist = Bucketlist(name=request_args.get('name'),
                                        created_by=self.current_user)
            session.add(new_bucketlist)
            session.commit()
            return 'Bucketlist successfully created', 200

        # Raised by Database API when the unique constraint on name is violated
        except IntegrityError:
            session.rollback()
            return 'Bucketlist name already exists', 409


class BucketlistDetail(Request, Resource):
    """
        Class based view that handles: display of a bucketlist's details using the GET http verb
        and updating of a bucketlist using the PUT http verb, as well as deleting
        using the DELETE http verb.
    """

    def get(self, bucketlist_id):
        """ Called for a GET request """
        if not self.is_authenticated():
            return 'Please login', 401

        bucketlist = Bucketlist.query.filter_by(id=bucketlist_id,
                                                created_by=self.current_user).first()
        if not bucketlist:
            return 'Bucketlist does not exist', 404

        if bucketlist.items:
            bucketlist_items = [{'id': item.id,
                                 'name': item.name,
                                 'done': item.completed} for item in bucketlist.items]
        else:
            bucketlist_items = 'None'

        bucketlist_detail = {'id': bucketlist.id,
                             'name': bucketlist.name,
                             'items': bucketlist_items,
                             'created_by': bucketlist.created_by.username,
                             'date_created': str(bucketlist.creation_date),
                             'date_modified': str(bucketlist.modification_date)}

        return bucketlist_detail, 200

    def put(self, bucketlist_id):
        """ Called for a PUT request """
        if not self.is_authenticated():
            return 'Please login', 401

        request_args = self.parse_args()
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if bucketlist and request_args.get('name'):
            try:
                # Update bucketlist name and commit to the database
                bucketlist.name = request_args.get('name')
                session.add(bucketlist)
                session.commit()
                return 'Bucketlist successfully updated', 200

            except IntegrityError:
                session.rollback()
                return 'Bucketlist name already exists', 409

        elif bucketlist and not request_args.get('name'):
            return 'Supply new bucketlist name', 400

        else:
            return 'Bucketlist does not exist', 404

    def delete(self, bucketlist_id):
        """ Called for a DELETE request """
        if not self.is_authenticated():
            return 'Please login', 401
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        session.delete(bucketlist)
        session.commit()
        return 'Bucketlist successfully deleted', 200


class BucketlistItems(Request, Resource):
    """
    View class used to display items in a particular bucketlist using the GET http verb;
     as well as create new items using the POST http verb.
    """

    def get(self, bucketlist_id):
        """ Called with the GET http verb """
        # Only authenticated users
        if not self.is_authenticated():
            return 'Please login', 401
        bucketlist = Bucketlist.query.filter_by(id=bucketlist_id,
                                                created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        bucketlist_items = Item.query.filter_by(bucketlist=bucketlist)

        # For a bucketlist with no items
        if not len(list(bucketlist_items)):
            return {'Items': 'None'}, 200

        bucketlist_items = [{'id': item.id,
                             'name': item.name,
                             'done': item.completed} for item in self.paginated(bucketlist_items)]
        return {'Items': bucketlist_items,
                'Page': '{} of {}'.format(self.page, self.total_pages)}, 200

    def post(self, bucketlist_id):
        """ Called with the POST http verb """
        # Only authenticated users
        if not self.is_authenticated():
            return 'Please login', 401
        request_args = self.parse_args()
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        if not request_args.get('name'):
            return 'Item name not supplied', 400

        try:
            new_item = Item(name=request_args.get('name'), bucketlist=bucketlist)

            session.add(new_item)
            session.commit()
            return 'New item added successfully', 200

        except IntegrityError:
            session.rollback()
            return 'Item name already exists', 409


class BucketListItemDetail(Request, Resource):
    """
        View class used to display an item's details using the GET http verb;
         as well as update items using the PUT http verb.
         Also deletes items using the DELETE http verb
    """
    def get(self, bucketlist_id, item_id):
        """ Called with a GET request """
        # Only authenticated users
        if not self.is_authenticated():
            return 'Please login', 401
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        item = Item.query.filter_by(id=item_id, bucketlist=bucketlist).first()
        if not item:
            return 'Item does not exist', 404

        item_detail = {'id': item.id,
                       'name': item.name,
                       'done': item.completed,
                       'creation_date': str(item.creation_date),
                       'last_modified': str(item.modification_date)}
        return item_detail, 200

    def put(self, bucketlist_id, item_id):
        """ Called with a PUT request """
        # Only authenticated users
        if not self.is_authenticated():
            return 'Please login', 401

        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        request_args = self.parse_args()

        # Missing item name
        if not request_args.get('name') and not request_args.get('done'):
            return 'Item name needed', 400

        item = session.query(Item).filter_by(id=item_id,
                                             bucketlist=bucketlist).first()

        if not item:
            return 'Item does not exist', 404

        try:
            if request_args.get('name'):
                item.name = request_args.get('name')

            if request_args.get('done'):
                item.completed = request_args.get('done')

            session.add(item)
            session.commit()
            return 'Item updated', 200

        except IntegrityError:
            session.rollback()
            return 'Item name already exists', 409

    def delete(self, bucketlist_id, item_id):
        """ Called with a DELETE request """
        # Only authenticated users
        if not self.is_authenticated():
            return 'Please login', 401
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        item = session.query(Item).filter_by(id=item_id,
                                             bucketlist=bucketlist).first()
        if not item:
            return 'Item does not exist', 404

        session.delete(item)
        session.commit()
        return 'Item deleted', 200

