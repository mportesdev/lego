from unittest.mock import patch

from django.core.management import call_command
from django.test import TransactionTestCase

from lego.images import store_image

from . import test_settings


@test_settings
class TestTasks(TransactionTestCase):
    def test_enqueue_and_run(self):
        result = store_image.enqueue(1)
        self.assertEqual(result.status, "READY")

        with patch("lego.images._store_image") as mock:
            call_command("db_worker", max_tasks=1)

        mock.assert_called_once()
        result.refresh()
        self.assertEqual(result.status, "SUCCESSFUL")
