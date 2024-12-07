from unittest.mock import patch

from requests import HTTPError


def _mock_func(set_lego_id):
    if set_lego_id == "1234-1":
        return {"name": "Fighter Jet", "image_url": "img1234-1.jpg"}
    if set_lego_id == "999-1":
        raise HTTPError("404 Client Error: Not Found")
    raise ValueError("_mock_func: unexpected test argument")


def get_set_info_mock():
    return patch("lego.views.get_set_info", side_effect=_mock_func)


def _mock_generator(set_lego_id):
    if set_lego_id == "1234-1":
        yield {
            "lego_id": "333",
            "name": "Pilot",
            "image_url": "img333.jpg",
            "quantity": 1,
        }
        yield {
            "lego_id": "111",
            "name": "Jet Engine",
            "color_name": "Blue",
            "image_url": "img111b.jpg",
            "quantity": 1,
        }
        yield {
            "lego_id": "222",
            "name": "Wheel",
            "color_name": "Black",
            "image_url": "img222k.jpg",
            "quantity": 1,
            "is_spare": True,
        }
        yield {
            "lego_id": "222",
            "name": "Wheel",
            "color_name": "Black",
            "image_url": "img222k.jpg",
            "quantity": 3,
            "is_spare": False,
        }
        yield {
            "lego_id": "234pr",
            # shape name for this lego_id differs from db, must be updated
            "name": "Brick 2 x 4 with studs",
            "color_name": "Blue",
            "image_url": "img234prB.jpg",
            "quantity": 1,
            "is_spare": False,
        }
        yield {
            "lego_id": "102",
            "name": "Plate 1 x 3",
            "color_name": "White",
            # image url for this part differs from db, must be updated
            "image_url": "img102W2.jpg",
            "quantity": 1,
            "is_spare": False,
        }
    else:
        raise ValueError("_mock_generator: unexpected test argument")


def get_set_parts_mock():
    return patch("lego.views.get_set_parts", side_effect=_mock_generator)
