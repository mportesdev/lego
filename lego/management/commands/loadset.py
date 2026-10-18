from django.core.management.base import LabelCommand

from lego.api_calls import get_set_data
from lego.orm_utils import get_set, save_set_with_parts


class Command(LabelCommand):
    help = (
        "Add a new set or update an existing one by retrieving fresh data"
        " from the external API."
    )
    label = "lego_id"

    def handle_label(self, lego_id, **options):
        try:
            set_data = get_set_data(lego_id)
        except OSError:
            self.stdout.write(f"Data not found: {lego_id}")
            return

        set_, created = get_set(lego_id)
        if not created:
            self.stdout.write(f"Updating existing set:\n{set_!r}")
            new_name = set_data["info"]["name"]
            if set_.name != new_name:
                self.stdout.write(f"Set name changed: {new_name}")
            new_url = set_data["info"]["image_url"]
            if set_.image.origin_url != new_url:
                self.stdout.write(f"Set image URL changed: {new_url}")
            set_.parts.clear()

        save_set_with_parts(set_, set_data)
