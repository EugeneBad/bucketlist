from app.app import app, db
import unittest
import json


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.create_all()
        register_user = self.app.post('api/V1/auth/register',
                                      data={'username': 'admin', 'password': 'admin'})
        self.auth_token = json.loads(register_user.data.decode()).get('auth_token')

    def tearDown(self):
        db.drop_all()
