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
