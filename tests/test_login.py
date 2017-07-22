import json
from . test_base import BaseTest


class TestLoginView(BaseTest):

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
