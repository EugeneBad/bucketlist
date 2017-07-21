from . test_base import BaseTest
from itertools import cycle
import json


class TestBucketlistItems(BaseTest):
    def setUp(self):
        super().setUp()
        self.app.post('api/V1/bucketlists',
                      headers={'token': self.auth_token},
                      data={'name': 'Travel'})

        for city in ['Tokyo', 'Utah', 'Venice', 'Warsaw', 'York']:
            self.app.post('api/V1/bucketlists/1/items',
                          headers={'token': self.auth_token},
                          data={'name': city})

    # Authentication required
    def test_authentication_requirement(self):
        get_response = self.app.get('api/V1/bucketlists/1/items')
        post_response = self.app.post('api/V1/bucketlists/1/items')
        self.assertEqual(get_response.status_code, 401,
                         msg='BucketlistItems view accepts unauthenticated GET requests')
        self.assertEqual(post_response.status_code, 401,
                         msg='BucketlistItems view accepts unauthenticated POST requests')

        get_response = self.app.get('api/V1/bucketlists/1/items',
                                    headers={'token': self.auth_token})

        self.assertEqual(get_response.status_code, 200,
                         msg='BucketlistItems view rejects authenticated users')

    # Create with missing name
    def test_fail_create_item_with_missing_name(self):
        post_response = self.app.post('api/V1/bucketlists/1/items',
                                      headers={'token': self.auth_token},
                                      data={'name': ''})
        self.assertEqual(post_response.status_code, 400,
                         msg='BucketlistItems view does not return 400 for POST with missing name')

    # Create with valid name
    def test_create_item_with_valid_name(self):
        post_response = self.app.post('api/V1/bucketlists/1/items',
                                      headers={'token': self.auth_token},
                                      data={'name': 'Beijing'})

        self.assertEqual(post_response.status_code, 200,
                         msg='BucketlistItems view does not create new bucketlist')

    # Create with duplicate name
    def test_fail_create_item_duplicate_name(self):
        duplicate_name_response = self.app.post('api/V1/bucketlists/1/items',
                                                headers={'token': self.auth_token},
                                                data={'name': 'Venice'})

        self.assertEqual(duplicate_name_response.status_code, 409,
                         msg='BucketlistItems view accepts a duplicate bucketlist name')

    # Response if items exist
    def test_response_on_existing_items(self):
        response = self.app.get('api/V1/bucketlists/1/items',
                                headers={'token': self.auth_token})

        self.assertEqual(response.status_code, 200,
                         msg='BucketlistItems view not successfully fetching items')

        response_content = json.loads(response.data.decode())
        self.assertEqual(len(response_content.get('Items')), 5,
                         msg='BucketlistItems view returns wrong number of items')

        expected_names = cycle(['Tokyo', 'Utah', 'Venice', 'Warsaw', 'York'])

        for item in response_content.get('Items'):
            self.assertEqual(item.get('name'), next(expected_names),
                             msg='Correct names of items not returned')
