import logging.config
import os
import re
from pathlib import Path
from unittest.mock import patch

from django.test import override_settings
from requests import HTTPError

test_settings = override_settings(
    STATIC_ROOT=Path(__file__).parent / "teststatic",
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ],
)

# note: logging settings cannot be simply overridden with `override_settings`
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "lego": {
                "level": "DEBUG",
                "handlers": ["test-logfile"],
            },
        },
        "handlers": {
            "test-logfile": {
                "class": "logging.FileHandler",
                "filename": os.getenv("LEGO_TEST_LOGFILE", os.devnull),
                "level": "DEBUG",
                "formatter": "detailed",
            },
        },
        "formatters": {
            "detailed": {
                "format": "{asctime} | {name} | {levelname} | {message}",
                "style": "{",
            },
        },
    }
)


class OrderedPartsMixin:
    def assertParts(self, text, *parts):
        regex = re.compile(
            ".*?".join(re.escape(part) for part in parts),
            flags=re.DOTALL,
        )
        self.assertRegex(text, regex)


def _set_info_mock(set_lego_id):
    if set_lego_id == "1234-1":
        return {"name": "Fighter Jet", "image_url": "test://cdn.test/img/1234.jpg"}
    elif set_lego_id == "1122-1":
        return {"name": "Miniset", "image_url": "test://cdn.test/img/1122.jpg"}
    raise HTTPError("404 Not Found")


def get_set_info_mock():
    return patch("lego.views.get_set_info", side_effect=_set_info_mock)


def _set_parts_mock(set_lego_id):
    if set_lego_id == "1234-1":
        yield {  # existing part
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "color_name": "White",
            "image_url": "test://cdn.test/img/2345W.jpg",
            "quantity": 2,
            "is_spare": False,
        }
        yield {  # part without color
            "lego_id": "fig-0006",
            "name": "Pilot, Blue Helmet",
            "image_url": "test://cdn.test/img/fig-0006.jpg",
            "quantity": 1,
        }
        yield {  # part without image
            "lego_id": "6868",
            "name": "Jet Engine",
            "color_name": "Blue",
            "image_url": None,
            "quantity": 1,
        }
        yield {  # new shape, new color
            "lego_id": "4242",
            "name": "Wheel",
            "color_name": "Black",
            "image_url": "test://cdn.test/img/4242K.jpg",
            "quantity": 3,
            "is_spare": False,
        }
        yield {  # spare part
            "lego_id": "4242",
            "name": "Wheel",
            "color_name": "Black",
            "image_url": "test://cdn.test/img/4242K.jpg",
            "quantity": 1,
            "is_spare": True,
        }
        yield {  # new part, existing shape, updated shape name
            "lego_id": "2345",
            "name": "Brick 2 x 4 new",
            "color_name": "Blue",
            "image_url": "test://cdn.test/img/2345B.jpg",
            "quantity": 1,
            "is_spare": False,
        }
        yield {  # existing part, updated image_url
            "lego_id": "23456",
            "name": "Plate 1 x 3",
            "color_name": "White",
            "image_url": "test://cdn.test/img/23456W2.jpg",
            "quantity": 1,
            "is_spare": False,
        }
    elif set_lego_id == "1122-1":
        yield {  # new shape, existing color
            "lego_id": "3344a",
            "name": "Brick 2 x 2",
            "color_name": "Red",
            "image_url": "test://cdn.test/img/3344aR.jpg",
            "quantity": 1,
            "is_spare": False,
        }


def get_set_parts_mock():
    return patch("lego.views.get_set_parts", side_effect=_set_parts_mock)
