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
        img = Image.open(io.BytesIO(response.content))

    scale_factor = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height)
    if scale_factor >= 1:
        return img

    scaled_img = img.resize(
        (round(img.width * scale_factor), round(img.height * scale_factor))
    )
    scaled_img.format = img.format
    return scaled_img


def _suffix_and_params(format):
    match format:
        case "JPEG" | "MPO":
            suffix = "jpg"
            params = {"quality": 92}
        case "PNG":
            suffix = "png"
            params = {"compress_level": 3}
        case _:
            suffix = None
            params = {}
    return suffix, params


def _store_image(model, subdir):
    obj = model.objects.filter(
        image__isnull=True, image_url__isnull=False
    ).order_by("-pk").first()
    if obj is None:
        logger.info(f"No {model.__name__} candidate to process")
        return

    image = _scaled_image_for_url(obj.image_url)
    suffix, params = _suffix_and_params(image.format)
    if suffix is None:
        logger.warning(f"Unexpected image format {image.format!r} for {obj!r}")
        return

    rel_path = Path("lego") / "img" / subdir / f"{obj.pk}.{suffix}"
    logger.info(f"Saving to static: {rel_path}")
    image.save(STATIC_DIR / rel_path, **params)

    obj.image = rel_path
    obj.save()


@task
def store_set_image():
    _store_image(LegoSet, "sets")


@task
def store_part_image():
    _store_image(LegoPart, "parts")
