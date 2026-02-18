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


def _info_stub(set_lego_id):
    if set_lego_id == "2001-1":
        return {"name": "Test Set 1", "image_url": "test://cdn.test/img/2001.jpg"}
    elif set_lego_id == "2002-1":
        return {"name": "Test Set 2", "image_url": "test://cdn.test/img/2002.jpg"}
    elif set_lego_id == "2003-1":
        return {"name": "Test Set 3", "image_url": "test://cdn.test/img/2003.jpg"}
    elif set_lego_id == "2004-1":
        return {"name": "Test Set 4", "image_url": "test://cdn.test/img/2004.jpg"}
    elif set_lego_id == "2005-1":
        return {"name": "Test Set 5", "image_url": "test://cdn.test/img/2005.jpg"}
    elif set_lego_id == "2006-1":
        return {"name": "Test Set 6", "image_url": "test://cdn.test/img/2006.jpg"}
    elif set_lego_id == "2007-1":
        return {"name": "Test Set 7", "image_url": "test://cdn.test/img/2007.jpg"}
    elif set_lego_id == "2008-1":
        return {"name": "Test Set 8", "image_url": "test://cdn.test/img/2008.jpg"}
    raise HTTPError("404 Not Found")


def get_set_info_mock():
    return patch("lego.views.get_set_info", side_effect=_info_stub)


def _parts_stub(set_lego_id):
    if set_lego_id == "2001-1":
        yield {  # new part (new shape, new color)
            "lego_id": "20001",
            "name": "Brick 1 x 1",
            "color_name": "Yellow",
            "image_url": "test://cdn.test/img/20001Y.jpg",
            "quantity": 1,
            "is_spare": False,
        }
        yield {  # existing part
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "color_name": "White",
            "image_url": "test://cdn.test/img/2345W.jpg",
            "quantity": 1,
            "is_spare": False,
        }
        yield {  # new part (existing shape, new color)
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "color_name": "Blue",
            "image_url": "test://cdn.test/img/2345B.jpg",
            "quantity": 1,
            "is_spare": False,
        }
        yield {  # new part (new shape, existing color)
            "lego_id": "20002",
            "name": "Brick 1 x 2",
            "color_name": "Red",
            "image_url": "test://cdn.test/img/20002R.jpg",
            "quantity": 1,
            "is_spare": False,
        }
    elif set_lego_id == "2002-1":
        yield {  # part with non-default quantity
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "color_name": "Red",
            "image_url": "test://cdn.test/img/2345R.jpg",
            "quantity": 10,
            "is_spare": False,
        }
    elif set_lego_id == "2003-1":
        yield {  # part followed by a spare part
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "color_name": "Red",
            "image_url": "test://cdn.test/img/2345R.jpg",
            "quantity": 5,
            "is_spare": False,
        }
        yield {  # spare part
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "color_name": "Red",
            "image_url": "test://cdn.test/img/2345R.jpg",
            "quantity": 1,
            "is_spare": True,
        }
    elif set_lego_id == "2004-1":
        yield {  # part with non-numeric lego_id
            "lego_id": "2345a",
            "name": "Brick 2 x 4",
            "color_name": "White",
            "image_url": "test://cdn.test/img/2345aW.jpg",
            "quantity": 1,
            "is_spare": False,
        }
    elif set_lego_id == "2005-1":
        yield {  # part without color
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "image_url": "test://cdn.test/img/2345.jpg",
            "quantity": 1,
            "is_spare": False,
        }
    elif set_lego_id == "2006-1":
        yield {  # part without image
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "color_name": "Blue",
            "image_url": None,
            "quantity": 1,
            "is_spare": False,
        }
    elif set_lego_id == "2007-1":
        yield {  # existing part, new image_url
            "lego_id": "2345",
            "name": "Brick 2 x 4",
            "color_name": "White",
            "image_url": "test://cdn.test/img/2345W2.jpg",
            "quantity": 1,
            "is_spare": False,
        }
    elif set_lego_id == "2008-1":
        yield {  # existing part, new shape name
            "lego_id": "2345",
            "name": "Brick 2 x 4 new",
            "color_name": "Red",
            "image_url": "test://cdn.test/img/2345R.jpg",
            "quantity": 1,
            "is_spare": False,
        }


def get_set_parts_mock():
    return patch("lego.orm_utils.get_set_parts", side_effect=_parts_stub)
