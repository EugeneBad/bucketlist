from itertools import cycle
from . test_base import BaseTest
import json


class BucketlistsTest(BaseTest):

    def setUp(self):
        super().setUp()
        for name in ['Food', 'Travel', 'People', 'Movies', 'Concerts']:
            self.app.post('api/V1/bucketlists',
                          headers={'token': self.auth_token},
                          data={'name': name})

    # Authentication required
    def test_authentication_requirement(self):
        get_response = self.app.get('api/V1/bucketlists')
        post_response = self.app.post('api/V1/bucketlists')
        self.assertTrue(get_response.status_code == 401,
                        msg='Bucketlists view accepts unauthenticated GET requests')
        self.assertTrue(post_response.status_code == 401,
                        msg='Bucketlists view accepts unauthenticated POST requests')

        get_response = self.app.get('api/V1/bucketlists',
                                    headers={'token': self.auth_token})

        self.assertEqual(get_response.status_code, 200,
                         msg='Bucketlists view rejects authenticated users')

    # Response if no bucketlist
    def test_response_before_adding_bucketlist(self):
        response = self.app.get('api/V1/bucketlists',
                                headers={'token': self.auth_token})
        self.assertEqual(response.status_code, 200)

    # Create with missing name
    def test_fail_create_bucketlist_with_missing_name(self):
        post_response = self.app.post('api/V1/bucketlists',
                                      headers={'token': self.auth_token},
                                      data={'name': ''})
        self.assertEqual(post_response.status_code, 400,
                         msg='Bucketlists view accepts creation with missing name')

    # Create with valid name
    def test_create_bucketlist_with_valid_name(self):
        post_response = self.app.post('api/V1/bucketlists',
                                      headers={'token': self.auth_token},
                                      data={'name': 'Cars'})

        self.assertEqual(post_response.status_code, 200,
                         msg='Bucketlists view does not create new bucketlist')

    # Create with duplicate name
    def test_fail_create_bucketlist_duplicate_name(self):

        duplicate_name_response = self.app.post('api/V1/bucketlists',
                                                headers={'token': self.auth_token},
                                                data={'name': 'Travel'})

        self.assertEqual(duplicate_name_response.status_code, 409,
                         msg='Bucketlists view accepts a duplicate bucketlist name')

    # Response if bucketlists exist
    def test_response_on_existing_bucketlists(self):

        response = self.app.get('api/V1/bucketlists',
                                headers={'token': self.auth_token})

        self.assertEqual(response.status_code, 200,
                         msg='Bucketlists view not successfully fetching bucketlists')

        response_content = json.loads(response.data.decode())
        self.assertEqual(len(response_content.get('Bucketlists')), 5,
                         msg='Bucketlists view returns wrong number of bucketlists')

        expected_names = cycle(['Food', 'Travel', 'People', 'Movies', 'Concerts'])

        for bucketlist in response_content.get('Bucketlists'):
            self.assertEqual(bucketlist.get('name'), next(expected_names),
                             msg='Correct names of bucketlists not returned')

    def test_pagination(self):
        response = self.app.get('api/V1/bucketlists?limit=3&page=1',
                                headers={'token': self.auth_token})

        response_content = json.loads(response.data.decode())
        self.assertEqual(len(response_content.get('Bucketlists')), 3,
                         msg='Bucketlists view returns wrong number of bucketlists per page')

        response = self.app.get('api/V1/bucketlists?limit=2&page=2',
                                headers={'token': self.auth_token})

        response_content = json.loads(response.data.decode())
        self.assertEqual(len(response_content.get('Bucketlists')), 2,
                         msg='Bucketlists view returns wrong number of bucketlists per page')


class TestBucketlistDetail(BaseTest):

    def setUp(self):
        super().setUp()
        for name in ['Food', 'Travel', 'People', 'Movies', 'Concerts']:
            self.app.post('api/V1/bucketlists',
                          headers={'token': self.auth_token},
                          data={'name': name})

    # Authentication requirement
    def test_authentication_requirement(self):
        get_response = self.app.get('api/V1/bucketlists/1')
        put_response = self.app.get('api/V1/bucketlists/1')
        delete_response = self.app.delete('api/V1/bucketlists/1')

        self.assertEqual(get_response.status_code, 401,
                        msg='BucketlistDetail view accepts unauthenticated GET requests')
        self.assertEqual(put_response.status_code, 401,
                        msg='BucketlistDetail view accepts unauthenticated PUT requests')
        self.assertEqual(delete_response.status_code, 401,
                        msg='BucketlistDetail view accepts unauthenticated DELETE requests')

    # Non existent bucketlist
    def test_get_response_non_existent_bucketlist(self):
        get_response = self.app.get('api/V1/bucketlists/94759485',
                                    headers={'token': self.auth_token})

        self.assertEqual(get_response.status_code, 404,
                         msg='404 not returned for non-existent bucketlists')

    # Getting existent bucketlist
    def test_get_response_when_bucketlist_existent(self):

        get_response = self.app.get('api/V1/bucketlists/1',
                                    headers={'token': self.auth_token})

        self.assertEqual(get_response.status_code, 200,
                         msg='BucketlistDetail does not return details of existent bucketlist')

    # Updating with no name
    def test_fail_when_update_name_empty(self):
        put_response = self.app.put('api/V1/bucketlists/1',
                                    headers={'token': self.auth_token}, data={'name': ''})

        self.assertEqual(put_response.status_code, 400,
                         msg='BucketlistDetail view does not reject updating with an empty name')

    # Updating with duplicate name
    def test_fail_when_update_name_duplicate(self):
        put_response = self.app.put('api/V1/bucketlists/1',
                                    headers={'token': self.auth_token},
                                    data={'name': 'Travel'})

        self.assertEqual(put_response.status_code, 409,
                         msg='BucketlistDetail view does not reject updating with a duplicate name')

    # Updating with valid name
    def test_update_with_new_bucketlist_name(self):
        put_response = self.app.put('api/V1/bucketlists/1',
                                    headers={'token': self.auth_token},
                                    data={'name': 'Cars'})

        self.assertEqual(put_response.status_code, 200,
                         msg='BucketlistDetail view does not update bucketlist name')

    # Successful deletion
    def test_deletion(self):
        delete_response = self.app.delete('api/V1/bucketlists/1',
                                    headers={'token': self.auth_token})

        self.assertEqual(delete_response.status_code, 200, msg='200 not returned for successful deletion')
        get_response = self.app.get('api/V1/bucketlists/1',
                                    headers={'token': self.auth_token})
        self.assertEqual(get_response.status_code, 404,
                         msg='DELETE request to BucketlistDetail does not delete bucketlist')
