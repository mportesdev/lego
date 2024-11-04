import logging

import requests

from project.settings import BASE_DIR

API_URL = "https://rebrickable.com/api/v3"
API_KEY = (BASE_DIR / ".rebrickable-key").read_text(encoding="utf8")

headers = {
    "Authorization": f"key {API_KEY}",
    "Accept": "application/json",
}

logger = logging.getLogger(__name__)


def get_set_info(set_lego_id):
    response = requests.get(
        f"{API_URL}/lego/sets/{set_lego_id}/", headers=headers, timeout=5
    )
    response.raise_for_status()
    data = response.json()
    return {
        "name": data["name"],
        "image_url": data["set_img_url"],
    }


def _get_paginated_data(url):
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    data = response.json()
    yield from data["results"]

    next_page_url = data.get("next")
    if next_page_url:
        yield from _get_paginated_data(next_page_url)


def _color_name_or_none(color_name):
    if color_name == "[No Color/Any Color]":
        return None
    return color_name


def get_set_parts(set_lego_id):
    for item in _get_paginated_data(f"{API_URL}/lego/sets/{set_lego_id}/minifigs/"):
        entry = {
            "lego_id": item["set_num"],
            "name": item["set_name"],
            "image_url": item["set_img_url"],
            "quantity": item["quantity"],
        }
        logger.debug(entry)
        yield entry

    for item in _get_paginated_data(f"{API_URL}/lego/sets/{set_lego_id}/parts/"):
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
