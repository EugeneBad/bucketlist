from . test_base import BaseTest
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
