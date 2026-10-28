from django.core.management.base import LabelCommand

from lego.api_calls import get_set_data
from lego.orm_utils import get_set, get_set_if_exists, save_set_with_parts


class Command(LabelCommand):
    help = (
        "Add a new set or update an existing one by retrieving fresh data"
        " from the external API."
    )
    label = "lego_id"

    def handle_label(self, lego_id, **options):
        set_ = get_set_if_exists(lego_id=lego_id)
        if set_:
            self.stdout.write(f"Already exists: {set_!r}")
            return

        try:
            set_data = get_set_data(lego_id)
        except OSError:
            self.stdout.write(f"Data not found: {lego_id}")
            return

        set_, created = get_set(lego_id)
        save_set_with_parts(set_, set_data)
