import io
import logging
import os
from pathlib import Path

import requests
from django.core.files.storage import storages
from django.tasks import task
from PIL import Image

from .models import LegoPart, LegoSet

DEFAULT_IMAGE_FORMAT = "webp"
MAX_WIDTH = 384
MAX_HEIGHT = 384

headers = {"Accept": "image/*"}

logger = logging.getLogger(__name__)


def _download_image(url):
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content))


def _scale_down(img):
    scale_factor = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height)
    if scale_factor >= 1:
        return img

    scaled_img = img.resize(
        (round(img.width * scale_factor), round(img.height * scale_factor))
    )
    scaled_img.format = img.format
    return scaled_img


def _save_to_media(image, rel_path):
    logger.info(f"Saving to media: {rel_path}")
    stream = io.BytesIO()
    image.save(stream, format=DEFAULT_IMAGE_FORMAT)
    storages["default"].save(rel_path, stream)


def _store_image(model, pk, subdir):
    obj = model.objects.get(pk=pk)
    obj_image = obj.image
    if obj_image is None or obj_image.origin_url is None:
        logger.info(f"No image URL: {obj!r}")
        return

    try:
        image = _download_image(obj_image.origin_url)
    except OSError as err:    # e.g. requests.HTTPError, PIL.UnidentifiedImageError
        logger.error(f"{err!r} reading image URL for {obj!r}")
        return
    else:
        image = _scale_down(image)

    rel_path = Path("lego") / "img" / subdir / f"{pk}.{DEFAULT_IMAGE_FORMAT}"
    _save_to_media(image, rel_path)
    obj_image.path = os.fspath(rel_path)
    obj_image.save()


@task
def store_set_image(pk):
    _store_image(LegoSet, pk, "sets")


@task
def store_part_image(pk):
    _store_image(LegoPart, pk, "parts")
