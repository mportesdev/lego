from unittest.mock import patch

from django.test import TestCase

from lego.images import _store_image
from lego.models import LegoPart


class TestStoreImage(TestCase):
    fixtures = ["test_data"]

    def test_store_image_skips_object_without_image_url(self):
        with (
            patch("lego.images._scaled_image_for_url") as mocked_func,
            self.assertLogs("lego.images", "INFO"),
        ):
            pk = LegoPart.objects.filter(image_url__isnull=True).first().pk
            _store_image(LegoPart, pk, "parts")

        mocked_func.assert_not_called()
