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
