from django.core.management.base import LabelCommand

from lego.api_calls import get_set_info
from lego.models import LegoSet
from lego.orm_utils import save_set_with_parts


class Command(LabelCommand):
    help = (
        "Add a new set or update an existing one by retrieving fresh data"
        " from the external API."
    )
    label = "lego_id"

    def handle_label(self, lego_id, **options):
        set_info = get_set_info(lego_id)

        set_, created = LegoSet.objects.get_or_create(lego_id=lego_id)
        if not created:
            self.stdout.write(f"Updating existing set:\n{set_!r}")
            if set_.name != set_info["name"]:
                self.stdout.write(f"Set name changed: {set_info["name"]}")
            if set_.image_url != set_info["image_url"]:
                self.stdout.write(f"Set image URL changed: {set_info["image_url"]}")

        save_set_with_parts(set_, set_info, is_new=created)
