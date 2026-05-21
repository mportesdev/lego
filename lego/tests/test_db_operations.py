from django.test import TestCase

from lego.tests import test_settings


@test_settings
class TestNumberOfQueries(TestCase):
    fixtures = ["test_data"]

    def test_search_in_all_mode(self):
        with self.assertNumQueries(2):    # 1 LegoSet query + 1 LegoPart query
            self.client.get(
                "/lego/search/", query_params={"q": "brick", "mode": "all"}
            )

    def test_search_in_name_mode(self):
        with self.assertNumQueries(2):    # 1 LegoSet query + 1 LegoPart query
            self.client.get(
                "/lego/search/", query_params={"q": "brick", "mode": "name"}
            )

    def test_search_in_id_mode(self):
        with self.assertNumQueries(2):    # 1 LegoSet query + 1 LegoPart query
            self.client.get(
                "/lego/search/", query_params={"q": "2345", "mode": "id"}
            )

    def test_search_in_color_mode(self):
        with self.assertNumQueries(1):    # 1 LegoPart query
            self.client.get(
                "/lego/search/", query_params={"q": "red", "mode": "color"}
            )
