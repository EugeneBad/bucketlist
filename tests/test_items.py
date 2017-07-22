from .test_base import BaseTest
from itertools import cycle
import json


class TestBucketlistItems(BaseTest):

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

    def test_items_in_non_existent_bucketlist(self):
        get_response = self.app.get('api/V1/bucketlists/176897/items',
                                    headers={'token': self.auth_token})

        post_response = self.app.post('api/V1/bucketlists/87671/items',
                                      headers={'token': self.auth_token})

        self.assertTrue(get_response.status_code == post_response.status_code == 404,
                        msg='BucketlistItems view not return 404 for non-existent bucketlist')

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


class TestBucketlistItemDetail(BaseTest):

    # Authentication requirement
    def test_authentication_requirement(self):
        get_response = self.app.get('api/V1/bucketlists/1/items/1')
        put_response = self.app.put('api/V1/bucketlists/1/items/1')
        delete_response = self.app.delete('api/V1/bucketlists/1/items/1')

        self.assertEqual(get_response.status_code, 401,
                         msg='BucketlistItemDetail view accepts unauthenticated GET requests')
        self.assertEqual(put_response.status_code, 401,
                         msg='BucketlistItemDetail view accepts unauthenticated PUT requests')
        self.assertEqual(delete_response.status_code, 401,
                         msg='BucketlistItemDetail view accepts unauthenticated DELETE requests')

    # Item in non-existent bucketlist
    def test_fail_accessing_item_in_non_existent_bucketlist(self):
        get_response = self.app.get('api/V1/bucketlists/640523/items/1', headers={'token': self.auth_token})
        put_response = self.app.put('api/V1/bucketlists/640523/items/1', headers={'token': self.auth_token})
        delete_response = self.app.delete('api/V1/bucketlists/640523/items/1', headers={'token': self.auth_token})

        self.assertEqual(get_response.status_code, 404,
                         msg='404 not returned for GET request to BucketlistItemDetail view'
                             ' for non existent bucketlist')

        self.assertEqual(put_response.status_code, 404,
                         msg='404 not returned for PUT request to BucketlistItemDetail view '
                             'for non existent bucketlist')

        self.assertEqual(delete_response.status_code, 404,
                         msg='404 not returned for DELETE request to BucketlistItemDetail view '
                             'for non existent bucketlist')

    # Non existent item
    def test_get_response_non_existent_item(self):
        get_response = self.app.get('api/V1/bucketlists/1/items/94759485',
                                    headers={'token': self.auth_token})
        self.assertEqual(get_response.status_code, 404,
                         msg='404 not returned for non-existent item')

    # Getting existent item
    def test_get_response_when_item_existent(self):
        get_response = self.app.get('api/V1/bucketlists/1/items/1',
                                    headers={'token': self.auth_token})

        self.assertEqual(get_response.status_code, 200,
                         msg='BucketlistItemDetail does not return details of existent item')

    # Updating with no name
    def test_fail_when_update_name_empty(self):
        put_response = self.app.put('api/V1/bucketlists/1/items/1',
                                    headers={'token': self.auth_token}, data={'name': ''})

        self.assertEqual(put_response.status_code, 400,
                         msg='BucketlistItemDetail view does not reject updating item with an empty name')

    # Updating with duplicate name
    def test_fail_when_update_name_duplicate(self):
        put_response = self.app.put('api/V1/bucketlists/1/items/1',
                                    headers={'token': self.auth_token},
                                    data={'name': 'Warsaw'})

        self.assertEqual(put_response.status_code, 409,
                         msg='BucketlistItemDetail view does not return 409 for updating with a duplicate name')

    # Updating with valid name
    def test_update_with_new_item_details(self):
        name_put_response = self.app.put('api/V1/bucketlists/1/items/3',
                                         headers={'token': self.auth_token},
                                         data={'name': 'Lisbon'})

        done_put_response = self.app.put('api/V1/bucketlists/1/items/3',
                                         headers={'token': self.auth_token},
                                         data={'done': True})

        self.assertEqual(name_put_response.status_code, 200,
                         msg='BucketlistItemDetail view does not update item name')

        self.assertEqual(done_put_response.status_code, 200,
                         msg='BucketlistItemDetail view does not update item completion status')

    # Updating non-existent item
    def test_update_non_existent_bucketlist(self):
        put_response = self.app.put('api/V1/bucketlists/1/items/34523',
                                    headers={'token': self.auth_token},
                                    data={'name': 'Texas'})

        self.assertEqual(put_response.status_code, 404,
                         msg='BucketlistItemDetail view does not return 404 for updating non-existent item')

    # Successful deletion
    def test_deletion(self):
        delete_response = self.app.delete('api/V1/bucketlists/1/items/4',
                                          headers={'token': self.auth_token})

        self.assertEqual(delete_response.status_code, 200,
                         msg='200 not returned for successful deletion of item')
        get_response = self.app.get('api/V1/bucketlists/1/items/4',
                                    headers={'token': self.auth_token})
        self.assertEqual(get_response.status_code, 404,
                         msg='DELETE request to BucketlistItemDetail does not delete item')

    # Deleting non-existent item
    def test_delete_non_existent_item(self):
        delete_response = self.app.delete('api/V1/bucketlists/1/items/4674', headers={'token': self.auth_token})

        self.assertEqual(delete_response.status_code, 404,
                         msg='BucketlistItemDetail view does not return 404 for trying to delete non existent item')
