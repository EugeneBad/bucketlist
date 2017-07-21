import json
from . test_base import BaseTest


class TestRegisterView(BaseTest):
    # Does not accept non post methods
    def test_not_post_method(self):
        response = self.app.get('api/V1/auth/register')
        self.assertEqual(response.status_code, 405)

    # Missing arguments
    def test_missing_username_password(self):
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
        self.assertEqual(response.status_code, 200,
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


class TestLoginView(BaseTest):

    # Takes only post
    def test_non_post_methods(self):
        get_response = self.app.get('api/V1/auth/login')
        put_response = self.app.put('api/V1/auth/login')
        self.assertTrue(get_response.status_code == put_response.status_code == 405,
                        msg='Login view accepts other methods')

    # Missing credentials
    def test_missing_credentials(self):
        response = self.app.post('api/V1/auth/login')
        self.assertEqual(response.status_code, 400,
                         msg='Login view accepts missing username and password')

        response = self.app.post('api/V1/auth/login',
                                 data={'username': '', 'password': 'master'})
        self.assertEqual(response.status_code, 400,
                         msg='Login view accepts password with missing username')

        response = self.app.post('api/V1/auth/login',
                                 data={'username': 'master', 'password': ''})
        self.assertEqual(response.status_code, 400,
                         msg='Login view accepts username with missing password')

    # Invalid credentials
    def test_invalid_credentials(self):
        not_user_response = self.app.post('api/V1/auth/login',
                                          data={'username': 'slave', 'password': 'slave'})
        self.assertEqual(not_user_response.status_code, 400,
                         msg='Login view accepts non registered users')

        self.app.post('api/V1/auth/register',
                      data={'username': 'master', 'password': 'master'})
        response = self.app.post('api/V1/auth/login',
                                 data={'username': 'master', 'password': 'slave'})
        self.assertEqual(response.status_code, 400,
                         msg='Login view accepts invalid password')

    # Valid credentials
    def test_valid_credentials(self):
        self.app.post('api/V1/auth/register',
                      data={'username': 'slave', 'password': 'slave'})
        response = self.app.post('api/V1/auth/login',
                                 data={'username': 'slave', 'password': 'slave'})
        self.assertTrue(response.status_code == 200,
                        msg='Login view does not accept valid credentials')
        self.assertTrue(json.loads(response.data.decode()).get('auth_token'),
                        msg='Login view does not return auth token')

