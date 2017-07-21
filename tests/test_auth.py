import json
from . test_base import BaseTest


class TestRegisterView(BaseTest):
    # Does not accept non post methods
    def test_not_post_method(self):
        response = self.app.get('api/V1/auth/register')
        self.assertEqual(response.status_code, 405)