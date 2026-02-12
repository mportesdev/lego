from django.test import TestCase, tag

from . import test_settings


@tag("login")
@test_settings
class TestSessionAuth(TestCase):
    fixtures = ["test_user"]

    def test_login(self):
        # not logged in
        self.assertNotIn("_auth_user_id", self.client.session)

        self.client.post(
            "/lego/login/", data={"username": "test-user", "password": "test-password"}
        )

        # logged in
        self.assertEqual(self.client.session["_auth_user_id"], "1")

    def test_failed_login(self):
        self.client.post(
            "/lego/login/", data={"username": "unknown-user", "password": "test-password"}
        )

        # not logged in
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout(self):
        self.client.login(username="test-user", password="test-password")
        # logged in
        self.assertIn("_auth_user_id", self.client.session)

        self.client.post("/lego/logout/")

        # not logged in
        self.assertNotIn("_auth_user_id", self.client.session)
