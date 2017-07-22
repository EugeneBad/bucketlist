import unittest
import jwt
from app.app import app, db, session
from app.db.models import Bucketlist, Item, User


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.create_all()

        test_user = User(username='admin', password='admin')

        for name in ['Food', 'Travel', 'People', 'Movies', 'Concerts']:
            session.add(Bucketlist(name=name, created_by=test_user))
            session.commit()

        self.auth_token = jwt.encode({'username': 'admin'}, app.config.get('SECRET_KEY'))

    def tearDown(self):
        db.drop_all()
