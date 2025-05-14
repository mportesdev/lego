from unittest.mock import patch

from django.test import TestCase, tag

from lego.images import _store_image
from lego.models import LegoPart

from . import test_settings, OrderedPartsMixin, get_set_info_mock, get_set_parts_mock


@test_settings
class TestAddSet(TestCase, OrderedPartsMixin):
    fixtures = ["test_data", "test_user"]

    @tag("write-db")
    def test_add_set(self):
        self.client.login(username="test-user", password="test-password")
        with (
            get_set_info_mock(),
            get_set_parts_mock(),
            self.assertLogs("lego.views", "INFO") as log_obj,
        ):
            self.client.post("/lego/set/add/", data={"set_lego_id": "1234-1"})

        log_output = "\n".join(log_obj.output)
        self.assertParts(
            log_output,
            "INFO", "Created: LegoSet",
            "INFO", "Created: Shape",
            "INFO", "Created: LegoPart",
            "INFO", "Created: Color",
            "INFO", "Skipping spare part:",
            "WARNING", "Outdated: Shape",
            "WARNING", "Updated: Shape",
            "WARNING", "Outdated: LegoPart",
            "WARNING", "Updated: LegoPart",
        )

    def test_existing_lego_id(self):
        self.client.login(username="test-user", password="test-password")
        with (
            get_set_info_mock(),
            get_set_parts_mock(),
            self.assertLogs("lego.views", "WARNING") as log_obj,
        ):
            self.client.post("/lego/set/add/", data={"set_lego_id": "123-1"})

        log_output = "\n".join(log_obj.output)
        self.assertParts(log_output, "WARNING", "Already exists: LegoSet")

    def test_invalid_lego_id(self):
        self.client.login(username="test-user", password="test-password")
        with (
            get_set_info_mock(),
            get_set_parts_mock(),
            self.assertLogs("lego.views", "ERROR") as log_obj,
        ):
            self.client.post("/lego/set/add/", data={"set_lego_id": "999-1"})

        log_output = "\n".join(log_obj.output)
        self.assertParts(
            log_output, "ERROR", "Error calling external API:", "Not Found",
        )


@test_settings
class TestStoreImage(TestCase, OrderedPartsMixin):
    fixtures = ["test_data"]

    def test_object_without_image_url(self):
        pk = LegoPart.objects.filter(image_url__isnull=True).first().pk
        with self.assertLogs("lego.images", "INFO") as log_obj:
            _store_image(LegoPart, pk, "parts")

        log_output = "\n".join(log_obj.output)
        self.assertParts(log_output, "INFO", "No image URL: LegoPart")

    def test_unknown_image_data(self):
        pk = LegoPart.objects.filter(image_url__isnull=False).first().pk
        with (
            patch("lego.images._scaled_image_for_url", side_effect=OSError),
            self.assertLogs("lego.images", "INFO") as log_obj,
        ):
            _store_image(LegoPart, pk, "parts")

        log_output = "\n".join(log_obj.output)
        self.assertParts(
            log_output,
            "ERROR", "reading image URL for LegoPart",
            "INFO", "Deleted `image_url`: LegoPart",
        )

    def test_unknown_image_format(self):
        pk = LegoPart.objects.filter(image_url__isnull=False).first().pk
        with (
            patch("lego.images.Image.Image", autospec=True, format="TEST") as image,
            patch("lego.images._scaled_image_for_url", return_value=image),
            self.assertLogs("lego.images", "INFO") as log_obj,
        ):
            _store_image(LegoPart, pk, "parts")

        log_output = "\n".join(log_obj.output)
        self.assertParts(
            log_output,
            "WARNING", "Unexpected image format 'TEST'",
            "INFO", "Deleted `image_url`: LegoPart",
        )


@test_settings
class TestAuth(TestCase, OrderedPartsMixin):
    fixtures = ["test_user"]

    @tag("login")
    def test_login(self):
        with self.assertLogs("lego.views", "INFO") as log_obj:
            self.client.post(
                "/lego/login/",
                data={"username": "test-user", "password": "test-password"},
            )

        log_output = "\n".join(log_obj.output)
        self.assertParts(log_output, "INFO", "User logged in: test-user")

    @tag("login")
    def test_login_with_incorrect_password(self):
        with self.assertLogs("lego.views", "INFO") as log_obj:
            self.client.post(
                "/lego/login/",
                data={"username": "test-user", "password": "bad-password"},
            )

        log_output = "\n".join(log_obj.output)
        self.assertParts(log_output, "INFO", "Failed user login: test-user")

    @tag("login")
    def test_login_with_incorrect_username(self):
        with self.assertLogs("lego.views", "INFO") as log_obj:
            self.client.post(
                "/lego/login/",
                data={"username": "unknown-user", "password": "test-password"},
            )

        log_output = "\n".join(log_obj.output)
        self.assertParts(log_output, "INFO", "Failed user login: unknown-user")

    @tag("login")
    def test_logout(self):
        self.client.login(username="test-user", password="test-password")
        with self.assertLogs("lego.views", "INFO") as log_obj:
            self.client.post("/lego/logout/")

        log_output = "\n".join(log_obj.output)
        self.assertParts(log_output, "INFO", "User logged out: test-user")
