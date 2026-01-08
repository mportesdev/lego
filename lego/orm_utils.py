import logging

from .api_calls import get_set_parts
from .images import store_set_image, store_part_image
from .models import Shape, Color, Image, LegoPart

logger = logging.getLogger(__name__)


def save_set_with_parts(set_, set_info, is_new=True):
    image_url = set_info["image_url"]
    image_outdated = image_url and (set_.image is None or set_.image.origin_url != image_url)
    if image_outdated:
        set_.image = _get_image(image_url)

    set_.name = set_info["name"]
    set_.save()
    if is_new:
        logger.info(f"Created: {set_!r}")
    if image_outdated:
        store_set_image.enqueue(pk=set_.pk)

    for item in get_set_parts(set_.lego_id):
        if item.get("is_spare"):
            logger.info(f"Skipping spare part: {item["name"]}, {item.get("color_name")}")
            continue
        shape = _get_shape(lego_id=item["lego_id"], name=item["name"])
        color_name = item.get("color_name")
        if color_name:
            color, created = Color.objects.get_or_create(name=color_name)
            if created:
                logger.info(f"Created: {color!r}")
        else:
            color = None
        part = _get_part(shape=shape, color=color, image_url=item["image_url"])
        set_.parts.add(part, through_defaults={"quantity": item["quantity"]})


def _get_shape(lego_id, name):
    """Get, update or create a `Shape` with given `lego_id` and `name`."""

    try:
        shape = Shape.objects.get(lego_id=lego_id)
        if shape.name != name:
            logger.warning(f"Outdated: {shape!r}")
            shape.name = name
            shape.save()
            logger.warning(f"Updated: {shape!r}")
    except Shape.DoesNotExist:
        shape = Shape.objects.create(lego_id=lego_id, name=name)
        logger.info(f"Created: {shape!r}")
    return shape


def _get_part(shape, color, image_url):
    """Get, update or create a `LegoPart` with given `shape`, `color` and
    image URL.
    """
    try:
        part = LegoPart.objects.get(shape=shape, color=color)
        if image_url and (part.image is None or part.image.origin_url != image_url):
            logger.warning(f"Outdated: {part!r}")
            part.image = _get_image(image_url)
            part.save()
            logger.warning(f"Updated: {part!r}")
            store_part_image.enqueue(pk=part.pk)
    except LegoPart.DoesNotExist:
        part = LegoPart.objects.create(
            shape=shape, color=color, image=_get_image(image_url)
        )
        logger.info(f"Created: {part!r}")
        store_part_image.enqueue(pk=part.pk)
    return part


def _get_image(url):
    """Get or create an `Image` with the given URL."""

    if not url:
        return None

    image, created = Image.objects.get_or_create(origin_url=url)
    if created:
        logger.info(f"Created: {image!r}")
    return image
