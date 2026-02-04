from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from lego.models import LegoSet

from . import test_settings, api_data_stub
from .factories import LegoSetFactory


def _get_set_data_mock():
    return patch(
        "lego.management.commands.loadset.get_set_data",
        side_effect=api_data_stub,
    )


@test_settings
class TestLoadSet(TestCase):
    @classmethod
    def setUpTestData(cls):
        LegoSetFactory.create(
            lego_id="111-1",
            name="Old Name",
            image__origin_url="test://cdn.test/img/111.jpg",
        )

    def test_existing_lego_id_skipped(self):
        with _get_set_data_mock() as mock:
            call_command("loadset", "111-1")

        mock.assert_not_called()

        # set not updated
        set_ = LegoSet.objects.get(lego_id="111-1")
        self.assertEqual(set_.name, "Old Name")

    def test_new_lego_id(self):
        with _get_set_data_mock() as mock:
            call_command("loadset", "2001-1")

        mock.assert_called_once_with("2001-1")

        # set added with parts
        set_ = LegoSet.objects.get(lego_id="2001-1")
        self.assertEqual(set_.name, "Test Set 1")
        self.assertEqual(set_.parts.count(), 4)
