from django.test import TestCase, tag

from lego.images import _store_image
from lego.models import LegoPart

from . import test_settings, ordered_regex, get_set_info_mock, get_set_parts_mock


@test_settings
class TestAddSet(TestCase):
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
        self.assertRegex(
            log_output,
            ordered_regex(
                "INFO", "Created: LegoSet",
                "INFO", "Skipping spare part:",
                "INFO", "Created: Shape",
                "INFO", "Created: Color",
                "INFO", "Created: LegoPart", "222",
                "WARNING", "Outdated: Shape",
                "WARNING", "Updated: Shape",
                "WARNING", "Outdated: LegoPart",
                "WARNING", "Updated: LegoPart",
            ),
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
        self.assertRegex(
            log_output,
            ordered_regex("WARNING", "Already exists: LegoSet"),
        )

    def test_invalid_lego_id(self):
        self.client.login(username="test-user", password="test-password")
        with (
            get_set_info_mock(),
            get_set_parts_mock(),
            self.assertLogs("lego.views", "ERROR") as log_obj,
        ):
            self.client.post("/lego/set/add/", data={"set_lego_id": "999-1"})

        log_output = "\n".join(log_obj.output)
        self.assertRegex(
            log_output,
            ordered_regex("ERROR", "Error calling external API:", "Not Found"),
        )


class TestStoreImage(TestCase):
    fixtures = ["test_data"]

    def test_object_without_image_url(self):
        with self.assertLogs("lego.images", "INFO") as log_obj:
            pk = LegoPart.objects.filter(image_url__isnull=True).first().pk
            _store_image(LegoPart, pk, "parts")

        log_output = "\n".join(log_obj.output)
        self.assertRegex(
            log_output,
            ordered_regex("INFO", "No image URL: LegoPart"),
        )
