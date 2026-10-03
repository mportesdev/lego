import shutil
from operator import attrgetter

from django.test import TestCase, tag

from . import (
    test_settings,
    OrderedPartsMixin,
    get_set_info_mock,
    get_set_parts_mock,
    prepare_assets,
)
from .factories import LegoPartFactory


@test_settings
class TestResponseStatus(TestCase):
    fixtures = ["test_data"]

    def test_index_page(self):
        response = self.client.get("/lego/")
        self.assertEqual(response.status_code, 200)

    def test_set_detail(self):
        response = self.client.get("/lego/set/123-1/")
        self.assertEqual(response.status_code, 200)

    def test_set_detail_not_found(self):
        response = self.client.get("/lego/set/999/")
        self.assertEqual(response.status_code, 404)

    def test_part_detail(self):
        response = self.client.get("/lego/part/fig-0008/")
        self.assertEqual(response.status_code, 200)

    def test_part_detail_with_color_id(self):
        response = self.client.get("/lego/part/2345/1/")
        self.assertEqual(response.status_code, 200)

    def test_part_detail_not_found_by_lego_id(self):
        response = self.client.get("/lego/part/999/")
        self.assertEqual(response.status_code, 404)

    def test_part_detail_not_found_by_color_id(self):
        response = self.client.get("/lego/part/2345/99/")
        self.assertEqual(response.status_code, 404)


@test_settings
class TestResponseContent(TestCase, OrderedPartsMixin):
    fixtures = ["test_data"]

    def test_index_page(self):
        response = self.client.get("/lego/")

        self.assertParts(
            response.text,
            "Latest Additions",
            "111-1 Airport",
        )
        self.assertParts(response.text, "123-1 Brick House")

    def test_set_detail(self):
        response = self.client.get("/lego/set/123-1/")

        self.assertParts(
            response.text,
            "Lego Set 123-1 Brick House",
            "Contains:",
            "1x", "fig-0008 Man, Brown Hat",
        )
        self.assertParts(response.text, "1x", "2345 Brick 2 x 4, Red")
        self.assertParts(
            response.text, "2x", "2345pr0001 Brick 2 x 4 with print, Red",
        )

    def test_part_detail(self):
        response = self.client.get("/lego/part/fig-0008/")

        self.assertParts(
            response.text,
            "Lego Part fig-0008 Man, Brown Hat",
            "Included in:",
            "1x in", "123-1 Brick House",
        )
        self.assertNotIn("All colors", response.text)

    def test_part_detail_with_color_id(self):
        response = self.client.get("/lego/part/2345/1/")

        self.assertParts(
            response.text,
            "Lego Part 2345 Brick 2 x 4, Red",
            "All colors",
            "Included in:",
            "1x in", "111-1 Airport",
        )
        self.assertParts(response.text, "1x in", "123-1 Brick House")


@test_settings
class TestResponseQuerySet(TestCase):
    fixtures = ["test_data"]

    def test_index_page(self):
        response = self.client.get("/lego/")

        self.assertQuerySetEqual(
            response.context["object_list"],
            (("111-1", "Airport"), ("123-1", "Brick House")),
            transform=attrgetter("lego_id", "name"),
            ordered=False,
        )

    def test_set_and_parts_found_by_name(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "brick", "mode": "name"}
        )

        self.assertQuerySetEqual(
            response.context["sets"],
            (("123-1", "Brick House"),),
            transform=attrgetter("lego_id", "name"),
        )
        self.assertQuerySetEqual(
            response.context["parts"],
            (("2345", "Red"), ("2345pr0001", "Red"), ("2345", "White")),
            transform=attrgetter("shape.lego_id", "color.name"),
            ordered=False,
        )

    def test_set_found_by_lego_id(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "123", "mode": "id"}
        )

        self.assertQuerySetEqual(
            response.context["sets"],
            (("123-1", "Brick House"),),
            transform=attrgetter("lego_id", "name"),
        )
        self.assertFalse(response.context["parts"])

    def test_parts_found_by_num_code(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "2345", "mode": "id"}
        )

        self.assertFalse(response.context["sets"])
        self.assertQuerySetEqual(
            response.context["parts"],
            (("2345", "Red"), ("2345pr0001", "Red"), ("2345", "White")),
            transform=attrgetter("shape.lego_id", "color.name"),
            ordered=False,
        )

    def test_parts_found_by_color(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "red", "mode": "color"}
        )

        self.assertFalse(response.context["sets"])
        self.assertQuerySetEqual(
            response.context["parts"],
            (("2345", "Red"), ("2345pr0001", "Red"), ("23456", "Red")),
            transform=attrgetter("shape.lego_id", "color.name"),
            ordered=False,
        )


@test_settings
class TestSearch(TestCase, OrderedPartsMixin):
    fixtures = ["test_data"]

    def test_set_found_by_name(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "house", "mode": "name"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'house'", response.text)
        self.assertParts(response.text, "123-1 Brick House")

    def test_set_found_by_name_in_all_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "house", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'house'", response.text)
        self.assertParts(response.text, "123-1 Brick House")

    def test_parts_found_by_name(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "plate", "mode": "name"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'plate'", response.text)
        self.assertParts(response.text, "23456 Plate 1 x 3, White")
        self.assertParts(response.text, "23456 Plate 1 x 3, Red")

    def test_set_and_parts_found_by_name(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "brick", "mode": "name"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'brick'", response.text)
        self.assertParts(
            response.text,
            "123-1 Brick House",
            "2345 Brick 2 x 4, Red",
        )
        self.assertParts(response.text, "2345 Brick 2 x 4, White")
        self.assertParts(response.text, "2345pr0001 Brick 2 x 4 with print, Red")

    def test_set_found_by_lego_id(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "123", "mode": "id"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for '123'", response.text)
        self.assertParts(response.text, "123-1 Brick House")

    def test_set_found_by_lego_id_in_all_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "123", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for '123'", response.text)
        self.assertParts(response.text, "123-1 Brick House")

    def test_parts_found_by_num_code(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "2345", "mode": "id"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for '2345'", response.text)
        self.assertParts(response.text, "2345 Brick 2 x 4, Red")
        self.assertParts(response.text, "2345 Brick 2 x 4, White")
        self.assertParts(response.text, "2345pr0001 Brick 2 x 4 with print, Red")
        self.assertNotIn("23456", response.text)

    def test_parts_found_by_num_code_in_all_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "2345", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for '2345'", response.text)
        self.assertParts(response.text, "2345 Brick 2 x 4, Red")
        self.assertParts(response.text, "2345 Brick 2 x 4, White")
        self.assertParts(response.text, "2345pr0001 Brick 2 x 4 with print, Red")
        self.assertNotIn("23456", response.text)

    def test_parts_found_by_color(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "red", "mode": "color"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'red'", response.text)
        self.assertParts(response.text, "2345 Brick 2 x 4, Red")
        self.assertParts(response.text, "2345pr0001 Brick 2 x 4 with print, Red")
        self.assertParts(response.text, "23456 Plate 1 x 3, Red")

    def test_parts_found_by_color_in_all_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "red", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'red'", response.text)
        self.assertParts(response.text, "2345 Brick 2 x 4, Red")
        self.assertParts(response.text, "2345pr0001 Brick 2 x 4 with print, Red")
        self.assertParts(response.text, "23456 Plate 1 x 3, Red")

    def test_nothing_found(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "999", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nothing Found", response.text)


@test_settings
class TestImageUrls(TestCase, OrderedPartsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        media_dir = prepare_assets()
        cls.addClassCleanup(shutil.rmtree, media_dir)

    @classmethod
    def setUpTestData(cls):
        LegoPartFactory.create(shape__lego_id="1001", color=None)
        LegoPartFactory.create(shape__lego_id="1002", color=None, image__path=None)
        LegoPartFactory.create(shape__lego_id="1003", color=None, image=None)

    def test_part_with_image_path_as_main_image(self):
        """LegoPart.image.path rendered via the main_image partial."""

        response = self.client.get("/lego/part/1001/")

        self.assertIn("media/lego/img/test", response.text)

    def test_part_with_image_path_as_item_image(self):
        """LegoPart.image.path rendered via the item_image partial."""

        response = self.client.get(
            "/lego/search/", query_params={"q": "1001", "mode": "id"}
        )

        self.assertIn("media/lego/img/test", response.text)

    def test_part_without_image_path_as_main_image(self):
        """`.image.path=None` rendered via the main_image partial."""

        response = self.client.get("/lego/part/1002/")

        self.assertIn("ti-lego", response.text)
        self.assertNotIn("test://", response.text)

    def test_part_without_image_path_as_item_image(self):
        """`.image.path=None` rendered via the item_image partial."""

        response = self.client.get(
            "/lego/search/", query_params={"q": "1002", "mode": "id"}
        )

        self.assertIn("ti-lego", response.text)
        self.assertNotIn("test://", response.text)

    def test_part_with_no_image_as_main_image(self):
        """`.image=None` rendered via the main_image partial."""

        response = self.client.get("/lego/part/1003/")
        self.assertIn("ti-lego", response.text)

    def test_part_with_no_image_as_item_image(self):
        """`.image=None` rendered via the item_image partial."""

        response = self.client.get(
            "/lego/search/", query_params={"q": "1003", "mode": "id"}
        )
        self.assertIn("ti-lego", response.text)


@test_settings
class TestAddSet(TestCase, OrderedPartsMixin):
    fixtures = ["test_data", "test_user"]

    @tag("login", "write-db")
    def test_basic_scenario(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "2001-1"}, follow=True
            )
            mock_1.assert_called_once_with("2001-1")
            mock_2.assert_called_once_with("2001-1")

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/set/add/")

        # go to the new set detail
        response = self.client.get("/lego/set/2001-1/")

        self.assertParts(
            response.text,
            "Lego Set 2001-1 Test Set 1",
            "Contains:",
            "1x", "20001 Brick 1 x 1, Yellow",
        )
        self.assertParts(response.text, "1x", "2345 Brick 2 x 4, White")
        self.assertParts(response.text, "1x", "2345 Brick 2 x 4, Blue")
        self.assertParts(response.text, "1x", "20002 Brick 1 x 2, Red")

    @tag("login", "write-db")
    def test_item_quantity(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock(), get_set_parts_mock():
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "2002-1"}, follow=True
            )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/set/add/")

        # go to the new set detail
        response = self.client.get("/lego/set/2002-1/")

        self.assertParts(response.text, "10x", "2345 Brick 2 x 4, Red")

    @tag("login", "write-db")
    def test_add_set_without_suffix(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "2001"}, follow=True
            )
            mock_1.assert_called_once_with("2001-1")
            mock_2.assert_called_once_with("2001-1")

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/set/add/")

    @tag("login")
    def test_add_set_existing_lego_id(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "123-1"}, follow=True
            )
            mock_1.assert_not_called()
            mock_2.assert_not_called()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/set/add/")

    @tag("login")
    def test_add_set_existing_lego_id_without_suffix(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "123"}, follow=True
            )
            mock_1.assert_not_called()
            mock_2.assert_not_called()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/set/add/")

    @tag("login")
    def test_add_set_invalid_lego_id(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "999-1"}, follow=True
            )
            mock_1.assert_called_once_with("999-1")
            mock_2.assert_not_called()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/set/add/")

    def test_add_set_redirects_to_login_if_not_logged_in(self):
        response = self.client.post(
            "/lego/set/add/", data={"set_lego_id": "2001-1"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/login/?next=/lego/set/add/")

    @tag("login", "write-db")
    def test_success_message(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock(), get_set_parts_mock():
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "2005-1"}, follow=True
            )

        self.assertIn("Added to queue: 2005-1 Test Set 5", response.text)

    @tag("login")
    def test_exists_message(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock(), get_set_parts_mock():
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "123-1"}, follow=True
            )

        self.assertIn("Already exists: 123-1 Brick House", response.text)

    @tag("login")
    def test_invalid_message(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock(), get_set_parts_mock():
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "999-1"}, follow=True
            )

        self.assertIn("Data not found: 999-1", response.text)


@test_settings
class TestAuth(TestCase, OrderedPartsMixin):
    fixtures = ["test_user"]

    def test_login_page(self):
        response = self.client.get("/lego/login/")

        self.assertEqual(response.status_code, 200)
        self.assertParts(response.text, "Username:", "Password:")

    @tag("login")
    def test_login_page_when_logged_in(self):
        self.client.login(username="test-user", password="test-password")
        response = self.client.get("/lego/login/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("You are already logged in", response.text)

    @tag("login")
    def test_login(self):
        response = self.client.get("/lego/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Log in", response.text)
        self.assertNotIn("Add a New Lego Set", response.text)
        self.assertNotIn("Admin Page", response.text)

        # log in
        response = self.client.post(
            "/lego/login/",
            data={"username": "test-user", "password": "test-password"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/")
        self.assertParts(response.text, "test-user", "Log out")
        self.assertIn("Add a New Lego Set", response.text)
        self.assertIn("Admin Page", response.text)

    @tag("login")
    def test_failed_login(self):
        response = self.client.post(
            "/lego/login/",
            data={"username": "unknown-user", "password": "test-password"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("enter a correct username", response.text)

    @tag("login")
    def test_logout(self):
        self.client.login(username="test-user", password="test-password")
        response = self.client.get("/lego/")
        self.assertIn("Log out", response.text)

        # log out
        response = self.client.post("/lego/logout/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/")
        self.assertIn("Log in", response.text)
        self.assertNotIn("Add a New Lego Set", response.text)
        self.assertNotIn("Admin Page", response.text)


@test_settings
class TestCommonContext(TestCase, OrderedPartsMixin):

    def test_common_context_rendered(self):
        response = self.client.get("/lego/")
        self.assertInHTML("Home | O&F Lego", response.text)
        self.assertParts(response.text, "Search:", "everywhere")

        response = self.client.get("/lego/login/")
        self.assertInHTML("Log in | O&F Lego", response.text)
        self.assertParts(response.text, "Search:", "everywhere")
