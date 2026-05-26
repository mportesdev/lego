from django.test import TestCase

from lego.tests import test_settings


@test_settings
class TestNumberOfQueries(TestCase):
    fixtures = ["test_data"]

    def test_index_page(self):
        with self.assertNumQueries(2):
            self.client.get("/lego/")

    def test_set_detail(self):
        """
        1. select LegoSet + related many-to-one (select_related)
        2. select SetItem (many-to-many) rows related to 1. (prefetch_related)
        3. select LegoPart rows related to 2.
        4. select Shape rows related to 3.
        5. select Color rows related to 3.
        6. select Image rows related to 3.
        """
        with self.assertNumQueries(6):
            self.client.get("/lego/set/123-1/")

    def test_part_detail(self):
        """
        1. select LegoPart + related many-to-one (select_related)
        2. select SetItem (many-to-many) rows related to 1. (prefetch_related)
        3. select LegoSet rows related to 2.
        4. select Image rows related to 3.
        """
        with self.assertNumQueries(4):
            self.client.get("/lego/part/2345/1/")

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
