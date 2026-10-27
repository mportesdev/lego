import shutil
from unittest.mock import patch, create_autospec

from django.test import TestCase
from PIL.Image import Image as PILImage

from lego.images import _scale_down, _save_to_media, _update_image_path, store_image_for_pk
from lego.models import Image

from . import test_settings, setup_media_subdir, dummy_image
from .factories import ImageFactory


@test_settings
class TestScaleDown(TestCase):
    def test_large_image_resized(self):
        img = create_autospec(PILImage, instance=True, width=768, height=384)
        _scale_down(img)

        img.resize.assert_called_once_with((384, 192))

    def test_small_image_not_resized(self):
        img = create_autospec(PILImage, instance=True, width=384, height=384)
        _scale_down(img)

        img.resize.assert_not_called()


@test_settings
class TestSaveToMedia(TestCase):
    def setUp(self):
        super().setUp()
        self.media_subdir = setup_media_subdir()
        self.addCleanup(shutil.rmtree, self.media_subdir)

    def test_image_saved_to_media(self):
        img = dummy_image()
        rel_path = "lego/img/test0099.webp"
        _save_to_media(img, rel_path)

        self.assertTrue((self.media_subdir / "img" / "test0099.webp").is_file())


@test_settings
class TestStoreImage(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_subdir = setup_media_subdir()
        cls.addClassCleanup(shutil.rmtree, cls.media_subdir)

    @classmethod
    def setUpTestData(cls):
        ImageFactory.create(pk=9999)
        ImageFactory.create(pk=1111)

    def test_skips_invalid_image_url(self):
        with (
            patch("lego.images._download_image", side_effect=OSError) as mock_1,
            patch("lego.images._scale_down") as mock_2,
        ):
            store_image_for_pk(9999)

        mock_1.assert_called()
        mock_2.assert_not_called()

    def test_image_saved_to_media(self):
        with patch("lego.images._download_image", return_value=dummy_image()):
            store_image_for_pk(9999)

        self.assertTrue((self.media_subdir / "img/00009999.webp").is_file())

    def test_image_path_saved_to_db(self):
        image = Image.objects.get(pk=1111)
        with patch("lego.images._download_image", return_value=dummy_image()):
            store_image_for_pk(1111)

        image.refresh_from_db()
        self.assertEqual(image.path, "lego/img/00001111.webp")


@test_settings
class TestUpdateImagePath(TestCase):
    @classmethod
    def setUpTestData(cls):
        ImageFactory.create(pk=1111)

    def test_image_path_updated(self):
        image = Image.objects.get(pk=1111)
        _update_image_path(1111, "lego/img/00001111.webp")

        image.refresh_from_db()
        self.assertEqual(image.path, "lego/img/00001111.webp")
