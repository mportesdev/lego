from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase

from lego.models import LegoSet
from lego.orm_utils import save_set_with_parts

from . import api_data_stub, test_settings


def _get_part_mock():
    return patch(
        "lego.orm_utils._get_part",
        side_effect=IntegrityError,
    )


@test_settings
class TestSaveSetWithParts(TestCase):
    def test_new_set_committed(self):
        set_data = api_data_stub("2006-1")
        save_set_with_parts(None, set_data)

        new_legoset = LegoSet.objects.get(lego_id="2006-1")
        self.assertEqual(new_legoset.parts.get().shape.lego_id, "2345")

    def test_new_set_rolled_back(self):
        set_data = api_data_stub("2006-1")
        with _get_part_mock():
            save_set_with_parts(None, set_data)

        self.assertFalse(LegoSet.objects.filter(lego_id="2006-1").exists())
