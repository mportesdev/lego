import io
import logging

import requests
from django.core.files.storage import storages
from PIL.Image import open as open_image

from .models import Image

DEFAULT_IMAGE_FORMAT = "webp"
MAX_WIDTH = 384
MAX_HEIGHT = 384

headers = {"Accept": "image/*"}

logger = logging.getLogger(__name__)


def _download_image(url):
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    return open_image(io.BytesIO(response.content))


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
    stream = io.BytesIO()
    image.save(stream, format=DEFAULT_IMAGE_FORMAT)
    actual_path = storages["default"].save(rel_path, stream)
    logger.info(f"Saved to media: {actual_path}")
    return actual_path


def _store_image(pk):
    image = Image.objects.get(pk=pk)
    try:
        pil_image = _download_image(image.origin_url)
    except OSError as err:    # e.g. requests.HTTPError, PIL.UnidentifiedImageError
        logger.error(f"{err!r} when reading image URL {image.origin_url!r}")
        return
    else:
        pil_image = _scale_down(pil_image)

    rel_path = f"lego/img/{image.pk:08d}.{DEFAULT_IMAGE_FORMAT}"
    rel_path = _save_to_media(pil_image, rel_path)
    image.path = rel_path
    image.save()
