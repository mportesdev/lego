import shutil
from unittest.mock import patch, create_autospec

from django.conf import settings
from django.test import TestCase
from PIL.Image import Image, new as new_image

from lego.images import _scale_down, _save_to_media, _store_image

from . import test_settings
from .factories import ImageFactory


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
class TestSaveToMedia(TestCase):
    def setUp(self):
        super().setUp()
        self.media_subdir = settings.MEDIA_ROOT / "lego"
        self.media_subdir.mkdir()
        self.addCleanup(shutil.rmtree, self.media_subdir)

    def test_image_saved_to_media(self):
        img = new_image("RGBA", (192, 192), color="#000")
        rel_path = "lego/img/test0099.webp"
        _save_to_media(img, rel_path)

        self.assertTrue((self.media_subdir / "img" / "test0099.webp").is_file())


@test_settings
class TestStoreImage(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_subdir = settings.MEDIA_ROOT / "lego"
        cls.media_subdir.mkdir()
        cls.addClassCleanup(shutil.rmtree, cls.media_subdir)

    @classmethod
    def setUpTestData(cls):
        ImageFactory.create(pk=9999)

    def test_skips_invalid_image_url(self):
        with (
            patch("lego.images._download_image", side_effect=OSError) as mock_1,
            patch("lego.images._scale_down") as mock_2,
        ):
            _store_image(9999)

        mock_1.assert_called()
        mock_2.assert_not_called()

    def test_image_saved_to_media(self):
        with patch(
            "lego.images._download_image",
            return_value=new_image("RGBA", (192, 192), color="#000"),
        ):
            _store_image(9999)

        self.assertTrue((self.media_subdir / "img/00009999.webp").is_file())
