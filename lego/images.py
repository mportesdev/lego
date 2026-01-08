import io
import logging
from pathlib import Path

import requests
from django_tasks import task
from PIL import Image

from .models import LegoPart, LegoSet

MAX_WIDTH = 384
MAX_HEIGHT = 384
STATIC_DIR = Path(__file__).parent / "static"

logger = logging.getLogger(__name__)


def _scaled_image_for_url(url):
    with requests.get(url) as response:
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))

    scale_factor = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height)
    if scale_factor >= 1:
        return img

    scaled_img = img.resize(
        (round(img.width * scale_factor), round(img.height * scale_factor))
    )
    scaled_img.format = img.format
    return scaled_img


def _delete_image_url(image):
    image.origin_url = None
    image.save()
    logger.info(f"Deleted `origin_url`: {image!r}")


def _store_image(model, pk, subdir):
    if pk is not None:
        obj = model.objects.get(pk=pk)
    else:
        obj = model.objects.filter(
            image__isnull=True, image_url__isnull=False
        ).order_by("-pk").first()
        if obj is None:
            logger.info(f"No {model.__name__} candidate to process")
            return

    obj_image = obj.image
    if obj_image is None or obj_image.origin_url is None:
        logger.info(f"No image URL: {obj!r}")
        return

    try:
        image = _scaled_image_for_url(obj_image.origin_url)
    except OSError as err:    # e.g. requests.HTTPError, PIL.UnidentifiedImageError
        logger.error(f"{err!r} reading image URL for {obj!r}")
        _delete_image_url(obj_image)
        return

    rel_path = Path("lego") / "img" / subdir / f"{obj.pk}.webp"
    logger.info(f"Saving to static: {rel_path}")
    image.save(STATIC_DIR / rel_path)

    obj_image.static_path = rel_path
    obj_image.save()


@task
def store_set_image(pk=None):
    _store_image(LegoSet, pk, "sets")


@task
def store_part_image(pk=None):
    _store_image(LegoPart, pk, "parts")
