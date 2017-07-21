from app.app import app, db
import unittest
import json


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.create_all()
        
    def tearDown(self):
        db.drop_all()

