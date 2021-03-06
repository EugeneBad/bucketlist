import json
from . test_base import BaseTest


class TestRegisterView(BaseTest):

    # Missing arguments
    def test_missing_both_username_and_password(self):
        response = self.app.post('api/V1/auth/register')
        self.assertEqual(response.status_code, 400,
                         msg='Register view accepts missing username and password')

        response = self.app.post('api/V1/auth/register',
                                 data={'other_arg_1': 'test', 'other_arg_2': 'test'})
        self.assertEqual(response.status_code, 400,
                         msg='Register view considers any arguments as username and password')

        response = self.app.post('api/V1/auth/register',
                                 data={'username': '', 'password': ''})
        self.assertEqual(response.status_code, 400,
                         msg='Register view accepts empty username and password')

    def test_missing_either_username_or_password(self):
        response = self.app.post('api/V1/auth/register',
                                 data={'username': 'master', 'password': ''})
        self.assertEqual(response.status_code, 400,
                         msg='Register view accepts username without password')

        response = self.app.post('api/V1/auth/register',
                                 data={'username': '', 'password': 'master'})
        self.assertEqual(response.status_code, 400,
                         msg='Register view accepts password without username')

    # Valid username and password
    def test_valid_username_password(self):
        response = self.app.post('api/V1/auth/register',
                                 data={'username': 'master', 'password': 'master'})
        self.assertEqual(response.status_code, 201,
                         msg='Register view not successful when valid credentials supplied')
        self.assertTrue(json.loads(response.data.decode()).get('auth_token'),
                        msg='Token not returned on successful registration')

    # Duplicate username
    def test_duplicate_username(self):
        self.app.post('api/V1/auth/register', data={'username': 'slave', 'password': 'slave'})
        response = self.app.post('api/V1/auth/register',
                                 data={'username': 'slave', 'password': 'slave'})

        self.assertEqual(response.status_code, 409,
                         msg='Register view accepts duplicate username')
