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


def _delete_image_url(obj):
    obj.image_url = None
    obj.save()
    logger.info(f"Deleted `image_url`: {obj!r}")


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

    try:
        image = _scaled_image_for_url(obj.image_url)
    except OSError as err:    # e.g. requests.HTTPError, PIL.UnidentifiedImageError
        logger.error(f"{err!r} reading image URL for {obj!r}")
        _delete_image_url(obj)
        return

    suffix, params = _suffix_and_params(image.format)
    if suffix is None:
        logger.warning(f"Unexpected image format {image.format!r} for {obj!r}")
        _delete_image_url(obj)
        return

    rel_path = Path("lego") / "img" / subdir / f"{obj.pk}.{suffix}"
    logger.info(f"Saving to static: {rel_path}")
    image.save(STATIC_DIR / rel_path, **params)

    obj.image = rel_path
    obj.save()


@task
def store_set_image(pk=None):
    _store_image(LegoSet, pk, "sets")


@task
def store_part_image(pk=None):
    _store_image(LegoPart, pk, "parts")
