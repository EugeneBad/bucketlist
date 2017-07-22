import unittest
import jwt
from app import app, db, session
from app.database.models import Bucketlist, Item, User


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.create_all()

        test_user = User(username='admin', password='admin')
        session.add(test_user)

        for name in ['Food', 'Travel', 'People', 'Movies', 'Concerts']:
            session.add(Bucketlist(name=name, created_by=test_user))

        test_bucketlist = session.query(Bucketlist).filter_by(id=1).first()

        for city in ['Tokyo', 'Utah', 'Venice', 'Warsaw', 'York']:
            session.add(Item(name=city, bucketlist=test_bucketlist))

        session.commit()
        self.auth_token = jwt.encode({'username': 'admin'}, app.config.get('SECRET_KEY'))

    def tearDown(self):
        db.drop_all()
