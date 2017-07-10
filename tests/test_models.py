import os
import unittest
from sqlalchemy import create_engine,engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date


os.environ['APP_SETTINGS'] = 'config.Testing'
from app.db.models import Bucketlist, Item


class TestBucketlistModel(unittest.TestCase):

    def setUp(self):
        # Create the database that will be used for testing

        self.engine = create_engine('sqlite:///test_db.sqlite3')

        # Launch a session to that database
        self.session = sessionmaker(bind=self.engine)()


        # Create several bucketlists in the test database
        bucketlist_1 = Bucketlist(name='travel',
                                  cd=datetime.now().date(),
                                  md=datetime.now().date(),
                                  cb='dom')

        bucketlist_2 = Bucketlist(name='eat',
                                  cd=datetime.now().date(),
                                  md=datetime.now().date(),
                                  cb='ell')

        self.session.add_all([bucketlist_1, bucketlist_2])
        self.session.commit()

    def test_bucketlist_model(self):
        some_bucketlist = Bucketlist.query.filter_by(id=2).first()
        self.assertEqual(some_bucketlist.name, 'eat', msg='Wrong bucketlist name retrieved')

        self.assertEqual(len(Bucketlist.query.all()), 2, msg='Correct number of bucketlists not created')

        self.assertEqual(some_bucketlist.cd, datetime.now().date(), msg='Wrong creation date retrieved')

        self.assertEqual(some_bucketlist.md, datetime.now().date(), msg='Wrong modification date retrieved')

        self.assertEqual(some_bucketlist.cb, 'ell', msg='Wrong bucketlist creator retrieved')

        some_bucketlist = self.session.query(Bucketlist).filter_by(id=1).first()
        some_bucketlist.name = 'drive'
        self.session.commit()

        same_bucketlist = Bucketlist.query.filter_by(id=1).first()
        self.assertEqual(same_bucketlist.name, 'drive', msg='Bucketlist name not updated')

        self.session.delete(some_bucketlist)
        self.session.commit()

        same_bucketlist = Bucketlist.query.filter_by(name='drive').first()
        self.assertTrue(same_bucketlist is None, msg='Bucketlist name not updated')


class TestItemsModel(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///test_db.sqlite3')

        # Launch a session to that database
        self.session = sessionmaker(bind=self.engine)()

        # Create several bucketlists in the test database
        bucketlist_1 = Bucketlist(name='travel',
                                  cd=datetime.now().date(),
                                  md=datetime.now().date(),
                                  cb='dom')

        item_1 = Item(name='paris',
                      cd=datetime.now().date(),
                      md=datetime.now().date(),
                      completed=False,
                      bucketlist_id=2)

        item_2 = Item(name='rome',
                      cd=datetime.now().date(),
                      md=datetime.now().date(),
                      completed=False,
                      bucketlist_id=2)

        self.session.add_all([bucketlist_1, item_1, item_2])
        self.session.commit()

    def test_items_model(self):
        some_item = Item.query.filter_by(id=2).first()
        self.assertEqual(some_item.name, 'rome', msg='Wrong item name retrieved')

        self.assertEqual(len(Item.query.all()), 2, msg='Correct number of items not created')

        self.assertEqual(some_item.cd, datetime.now().date(), msg='Wrong creation date retrieved')

        self.assertEqual(some_item.md, datetime.now().date(), msg='Wrong modification date retrieved')

        self.assertFalse(some_item.completed, msg='Wrong item completion status')

        some_item = self.session.query(Item).filter_by(id=1).first()
        some_item.name = 'prague'
        self.session.commit()

        same_item = Item.query.filter_by(id=1).first()
        self.assertEqual(same_item.name, 'prague', msg='Item name not updated')

        self.session.delete(some_item)
        self.session.commit()

        same_item = Item.query.filter_by(name='prague').first()
        self.assertTrue(same_item is None, msg='Bucketlist name not updated')

        some_bucketlist = self.session.query(Bucketlist).filter_by(id=2).first()

    def tearDown(self):
        # Delete the test database
        os.remove('test_db.sqlite3')

if __name__ == '__main__':
    unittest.main()
