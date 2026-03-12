from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from lego.views import add_set, search

from . import test_settings


@test_settings
class TestSearch(TestCase):
    fixtures = ["test_data"]

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_request_anonymous_user(self):
        request = self.factory.get(
            "/lego/search/", query_params={"q": "brick", "mode": "name"}
        )
        request.user = AnonymousUser()

        response = search(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Search Results", response.text)
        self.assertIn("Brick 2 x 4", response.text)


@test_settings
class TestAddSet(TestCase):
    fixtures = ["test_data", "test_user"]

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_request(self):
        request = self.factory.get("/lego/set/add/")
        request.user = User.objects.get()

        response = add_set(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Lego Set ID:", response.text)

    def test_get_request_anonymous_user(self):
        request = self.factory.get("/lego/set/add/")
        request.user = AnonymousUser()

        response = add_set(request)

        # redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
