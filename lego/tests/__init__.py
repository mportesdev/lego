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


def ordered_regex(*parts):
    return re.compile(
        ".*?".join(re.escape(part) for part in parts),
        flags=re.DOTALL,
    )


def _set_info_mock(set_lego_id):
    if set_lego_id == "1234-1":
        return {"name": "Fighter Jet", "image_url": "test://cdn.test/img/1234.jpg"}
    raise HTTPError("404 Not Found")


def get_set_info_mock():
    return patch("lego.views.get_set_info", side_effect=_set_info_mock)


def _set_parts_mock(set_lego_id):
    if set_lego_id == "1234-1":
        yield {  # part without color
            "lego_id": "333",
            "name": "Pilot",
            "image_url": "test://cdn.test/img/333.jpg",
            "quantity": 1,
        }
        yield {
            "lego_id": "111",
            "name": "Jet Engine",
            "color_name": "Blue",
            "image_url": "test://cdn.test/img/111b.jpg",
            "quantity": 2,
        }
        yield {  # spare part
            "lego_id": "222",
            "name": "Wheel",
            "color_name": "Black",
            "image_url": "test://cdn.test/img/222k.jpg",
            "quantity": 1,
            "is_spare": True,
        }
        yield {  # part without image
            "lego_id": "222",
            "name": "Wheel",
            "color_name": "Black",
            "image_url": None,
            "quantity": 3,
            "is_spare": False,
        }
        yield {  # part with an updated shape name compared to db
            "lego_id": "234pr",
            "name": "Brick 2 x 4 with studs",
            "color_name": "Blue",
            "image_url": "test://cdn.test/img/234prB.jpg",
            "quantity": 1,
            "is_spare": False,
        }
        yield {  # part with an updated image url compared to db
            "lego_id": "102",
            "name": "Plate 1 x 3",
            "color_name": "White",
            "image_url": "test://cdn.test/img/102W2.jpg",
            "quantity": 1,
            "is_spare": False,
        }


def get_set_parts_mock():
    return patch("lego.views.get_set_parts", side_effect=_set_parts_mock)
