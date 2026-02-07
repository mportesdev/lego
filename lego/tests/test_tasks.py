from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from lego.images import store_part_image

from . import test_settings


@test_settings
class TestTasks(TestCase):
    def test_enqueue_and_run(self):
        result = store_part_image.enqueue()
        self.assertEqual(result.status, "READY")

        with patch("lego.images._store_image") as mock:
            call_command("db_worker", max_tasks=1)

        mock.assert_called_once()
        result.refresh()
        self.assertEqual(result.status, "SUCCEEDED")
