from unittest.mock import patch

from django.test import TestCase

from lego.images import _store_image
from lego.models import LegoPart

from . import test_settings


@test_settings
class TestStoreImage(TestCase):
    fixtures = ["test_data"]

    def test_skips_object_without_image_url(self):
        pk = LegoPart.objects.filter(image_url__isnull=True).first().pk
        with patch("lego.images._scaled_image_for_url") as mock:
            _store_image(LegoPart, pk, "parts")

        mock.assert_not_called()

    def test_skips_unknown_image_data(self):
        pk = LegoPart.objects.filter(image_url__isnull=False).first().pk
        with (
            patch("lego.images._scaled_image_for_url", side_effect=OSError),
            patch("lego.images._suffix_and_params") as mock,
        ):
            _store_image(LegoPart, pk, "parts")

        mock.assert_not_called()

    def test_skips_unknown_image_format(self):
        pk = LegoPart.objects.filter(image_url__isnull=False).first().pk
        with (
            patch("lego.images.Image.Image", autospec=True, format="TEST") as image,
            patch("lego.images._scaled_image_for_url", return_value=image),
        ):
            _store_image(LegoPart, pk, "parts")

        image.save.assert_not_called()
