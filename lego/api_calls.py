import logging
import os

import requests
from requests.auth import AuthBase

API_URL = "https://rebrickable.com/api/v3"
API_KEY = os.getenv("REBRICKABLE_API_KEY")


class ApiAuth(AuthBase):
    def __call__(self, request):
        request.headers["Authorization"] = f"key {API_KEY}"
        return request


auth = ApiAuth()
headers = {"Accept": "application/json"}

logger = logging.getLogger(__name__)


def get_set_info(set_lego_id):
    data = _get_response(f"{API_URL}/lego/sets/{set_lego_id}/")
    return {
        "name": data["name"],
        "image_url": data["set_img_url"],
    }


def _get_paginated_data(url, session):
    data = _get_response(url, session)
    yield from data["results"]

    next_page_url = data.get("next")
    if next_page_url:
        yield from _get_paginated_data(next_page_url, session)


def _get_response(url, session=None):
    get_func = session.get if session else requests.get
    response = get_func(url, auth=auth, headers=headers, timeout=5)
    response.raise_for_status()
    return response.json()


def _color_name_or_none(color_name):
    if color_name == "[No Color/Any Color]":
        return None
    return color_name


def get_set_parts(set_lego_id):
    session = requests.Session()
    for item in _get_paginated_data(
        f"{API_URL}/lego/sets/{set_lego_id}/minifigs/", session
    ):
        entry = {
            "lego_id": item["set_num"],
            "name": item["set_name"],
            "image_url": item["set_img_url"],
            "quantity": item["quantity"],
        }
        logger.debug(entry)
        yield entry

    for item in _get_paginated_data(
        f"{API_URL}/lego/sets/{set_lego_id}/parts/", session
    ):
        entry = {
            "lego_id": item["part"]["part_num"],
            "name": item["part"]["name"],
            "color_name": _color_name_or_none(item["color"]["name"]),
            "image_url": item["part"]["part_img_url"],
            "quantity": item["quantity"],
            "is_spare": item["is_spare"],
        }
        logger.debug(entry)
        yield entry
