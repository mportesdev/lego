from unittest.mock import patch, create_autospec

from django.test import TestCase
from PIL.Image import Image

from lego.images import _scale_down, _store_image
from lego.models import LegoPart

from . import test_settings


@test_settings
class TestScaleDown(TestCase):
    def test_large_image_resized(self):
        img = create_autospec(Image, instance=True, width=768, height=384)
        _scale_down(img)

        img.resize.assert_called_once_with((384, 192))

    def test_small_image_not_resized(self):
        img = create_autospec(Image, instance=True, width=384, height=384)
        _scale_down(img)

        img.resize.assert_not_called()


@test_settings
class TestStoreImage(TestCase):
    fixtures = ["test_data"]

    def test_skips_object_without_image_url(self):
        pk = LegoPart.objects.filter(image__origin_url__isnull=True).first().pk
        with patch("lego.images._download_image") as mock:
            _store_image(LegoPart, pk, "parts")

        mock.assert_not_called()

    def test_skips_invalid_image_url(self):
        pk = LegoPart.objects.filter(image__origin_url__isnull=False).first().pk
        with (
            patch("lego.images._download_image", side_effect=OSError) as mock_1,
            patch("lego.images._scale_down") as mock_2,
        ):
            _store_image(LegoPart, pk, "parts")

        mock_1.assert_called()
        mock_2.assert_not_called()
