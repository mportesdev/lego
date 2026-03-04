from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from lego.views import add_set, search

from . import test_settings


@test_settings
class TestGetRequest(TestCase):
    fixtures = ["test_data"]

    def setUp(self):
        self.factory = RequestFactory()

    def test_search(self):
        request = self.factory.get(
            "/lego/search/", query_params={"q": "brick", "mode": "name"}
        )
        request.user = AnonymousUser()

        response = search(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Search Results", response.text)
        self.assertIn("Brick 2 x 4", response.text)

    def test_add_set_redirects_to_login_if_not_authenticated(self):
        request = self.factory.get("/lego/set/add/")
        request.user = AnonymousUser()

        response = add_set(request)

        self.assertEqual(response.status_code, 302)
        self.assertStartsWith(response.url, "/lego/login")
