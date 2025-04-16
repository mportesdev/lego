from django.test import TestCase, tag


class TestSessionAuth(TestCase):
    fixtures = ["test_user"]

    @tag("login")
    def test_login_and_logout(self):
        # not logged in
        self.assertNotIn("_auth_user_id", self.client.session)

        self.client.post(
            "/lego/login/", data={"username": "test-user", "password": "test-password"}
        )
        # logged in
        self.assertEqual(self.client.session["_auth_user_id"], "1")

        self.client.post("/lego/logout/")
        # not logged in
        self.assertNotIn("_auth_user_id", self.client.session)
