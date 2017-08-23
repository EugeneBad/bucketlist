from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from app.database.models import Bucketlist, Item, User
from app import session
from . utils import RequestMixin


class Register(RequestMixin, Resource):
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
        self.save(new_user)

        auth_token = self.generate_token(new_user.username)

        return {'auth_token': auth_token}, 201


class Login(RequestMixin, Resource):
    """ Class based view used to log in a user, accessible only via a POST request """
    def post(self):
        login_data = self.parse_args()

        # Both username and password have to be supplied
        if not login_data.get('username') or not login_data.get('password'):
            return 'Both username and password required', 401

        user = User.query.filter_by(username=login_data.get('username')).first()

        # User has to exist and password supplied has to be correct.
        if not user or self.set_password(login_data.get('password')) != user.password:
            return 'Check username and password', 401

        # Token payload is encoded with username and expiry date
        auth_token = self.generate_token(user.username)

        return {'auth_token': auth_token}, 200


class Bucketlists(RequestMixin, Resource):
    """
    Class based view that handles: display of bucketlists using the GET http verb
    and creation of bucketlists using the POST http verb
    """
    @RequestMixin.is_authenticated
    def get(self):
        """ Called for a GET request """
        bucketlists = Bucketlist.query.filter(Bucketlist.created_by == self.current_user).order_by(Bucketlist.id.desc())

        # When search phrase is supplied, re-filter bucketlists with 'contains' constraint
        if self.parse_args().get('q'):
            bucketlists = bucketlists.filter(Bucketlist.name.contains(self.parse_args().get('q').lower()))

        if not list(bucketlists):
            return {'Bucketlists': []}, 200

        paginated_list = self.paginated(bucketlists)

        # List comprehension that generates individual dictionaries of bucketlists
        list_of_bucketlists = [{'id': bucketlist.id,
                                'name': bucketlist.name.capitalize(),
                                'items': 0 if not bucketlist.items else len(bucketlist.items),
                                'date_created': str(bucketlist.creation_date),
                                'date_modified': str(bucketlist.modification_date),
                                'created_by': self.current_user.username} for bucketlist in paginated_list]
        return {'Bucketlists': list_of_bucketlists,
                'Page': '{} of {}'.format(self.page, self.total_pages),
                'has_next': self.has_next,
                'has_prev': self.has_prev}, 200

    @RequestMixin.is_authenticated
    def post(self):
        """ Called for a POST request """

        request_args = self.parse_args()

        if not request_args.get('name'):
            return 'Bucketlist name needed', 400

        try:
            new_bucketlist = Bucketlist(name=request_args.get('name').lower(),
                                        created_by=self.current_user)
            self.save(new_bucketlist)
            return 'Bucketlist successfully created', 200

        # Raised by Database API when the unique constraint on name is violated
        except IntegrityError:
            session.rollback()
            return 'Bucketlist name already exists', 409


class BucketlistDetail(RequestMixin, Resource):
    """
        Class based view that handles: display of a bucketlist's details using the GET http verb
        and updating of a bucketlist using the PUT http verb, as well as deleting
        using the DELETE http verb.
    """

    @RequestMixin.is_authenticated
    def get(self, bucketlist_id):
        """ Called for a GET request """

        bucketlist = Bucketlist.query.filter_by(id=bucketlist_id,
                                                created_by=self.current_user).first()
        if not bucketlist:
            return 'Bucketlist does not exist', 404

        if bucketlist.items:
            bucketlist_items = [{'id': item.id,
                                 'name': item.name,
                                 'done': item.completed} for item in bucketlist.items]
        else:
            bucketlist_items = []

        bucketlist_detail = {'id': bucketlist.id,
                             'name': bucketlist.name,
                             'items': bucketlist_items,
                             'created_by': bucketlist.created_by.username,
                             'date_created': str(bucketlist.creation_date),
                             'date_modified': str(bucketlist.modification_date)}

        return bucketlist_detail, 200

    @RequestMixin.is_authenticated
    def put(self, bucketlist_id):
        """ Called for a PUT request """

        request_args = self.parse_args()
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if bucketlist and request_args.get('name'):
            try:
                if bucketlist.name.lower() == request_args.get('name').lower():
                    return 'Bucketlist name already exists', 409

                # Update bucketlist name and commit to the database
                bucketlist.name = request_args.get('name').lower()
                self.save(bucketlist)
                return 'Bucketlist successfully updated', 200

            except IntegrityError:
                session.rollback()
                return 'Bucketlist name already exists', 409

        elif bucketlist and not request_args.get('name'):
            return 'Supply new bucketlist name', 400

        else:
            return 'Bucketlist does not exist', 404

    @RequestMixin.is_authenticated
    def delete(self, bucketlist_id):
        """ Called for a DELETE request """
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        self.remove(bucketlist)
        return 'Bucketlist successfully deleted', 200


class BucketlistItems(RequestMixin, Resource):
    """
    View class used to display items in a particular bucketlist using the GET http verb;
     as well as create new items using the POST http verb.
    """

    @RequestMixin.is_authenticated
    def get(self, bucketlist_id):
        """ Called with the GET http verb """
        bucketlist = Bucketlist.query.filter_by(id=bucketlist_id,
                                                created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        bucketlist_items = Item.query.filter(Item.bucketlist == bucketlist).order_by(Item.id.desc())

        # When search phrase is supplied, re-filter items with 'contains' constraint
        if self.parse_args().get('q'):
            bucketlist_items = bucketlist_items.filter(Item.name.contains(self.parse_args().get('q')))

        # For a bucketlist with no items
        if not list(bucketlist_items):
            return {'bucketlist_name': bucketlist.name, 'Items': []}, 200

        bucketlist_items = [{'id': item.id,
                             'name': item.name.capitalize(),
                             'done': item.completed,
                             'date_created': str(item.creation_date)} for item in self.paginated(bucketlist_items)]
        return {'bucketlist_name': bucketlist.name, 'Items': bucketlist_items,
                'Page': '{} of {}'.format(self.page, self.total_pages)}, 200

    @RequestMixin.is_authenticated
    def post(self, bucketlist_id):
        """ Called with the POST http verb """
        request_args = self.parse_args()
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        if not request_args.get('name'):
            return 'Item name not supplied', 400

        try:
            new_item = Item(name=request_args.get('name').lower(),
                            bucketlist=bucketlist)

            self.save(new_item)
            return 'New item added successfully', 200

        except IntegrityError:
            session.rollback()
            return 'Item name already exists', 409


class BucketListItemDetail(RequestMixin, Resource):
    """
        View class used to display an item's details using the GET http verb;
         as well as update items using the PUT http verb.
         Also deletes items using the DELETE http verb
    """

    @RequestMixin.is_authenticated
    def get(self, bucketlist_id, item_id):
        """ Called with a GET request """
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

    @RequestMixin.is_authenticated
    def put(self, bucketlist_id, item_id):
        """ Called with a PUT request """

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
                if request_args.get('name').lower() == item.name:
                    return 'Item name already exists', 409

                item.name = request_args.get('name').lower()

            if request_args.get('done'):
                item.completed = request_args.get('done')

            self.save(item)
            return 'Item updated', 200

        except IntegrityError:
            session.rollback()
            return 'Item name already exists', 409

    @RequestMixin.is_authenticated
    def delete(self, bucketlist_id, item_id):
        """ Called with a DELETE request """
        bucketlist = session.query(Bucketlist).filter_by(id=bucketlist_id,
                                                         created_by=self.current_user).first()

        if not bucketlist:
            return 'Bucketlist does not exist', 404

        item = session.query(Item).filter_by(id=item_id,
                                             bucketlist=bucketlist).first()
        if not item:
            return 'Item does not exist', 404

        self.remove(item)
        return 'Item deleted', 200
