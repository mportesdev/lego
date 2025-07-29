from operator import attrgetter

from django.test import TestCase, tag

from . import test_settings, OrderedPartsMixin, get_set_info_mock, get_set_parts_mock


@test_settings
class TestGetResponse(TestCase, OrderedPartsMixin):
    fixtures = ["test_data"]

    def test_index_page(self):
        response = self.client.get("/lego/")

        self.assertEqual(response.status_code, 200)
        self.assertParts(
            response.text,
            "Latest Additions",
            "111-1 Airport",
        )
        self.assertParts(response.text, "123-1 Brick House")

    def test_set_detail(self):
        response = self.client.get("/lego/set/123-1/")

        self.assertEqual(response.status_code, 200)
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

    def test_set_detail_not_found(self):
        response = self.client.get("/lego/set/999/")

        self.assertEqual(response.status_code, 404)

    def test_part_detail(self):
        response = self.client.get("/lego/part/fig-0008/")

        self.assertEqual(response.status_code, 200)
        self.assertParts(
            response.text,
            "Lego Part fig-0008 Man, Brown Hat",
            "Included in:",
            "1x in", "123-1 Brick House",
        )
        self.assertNotIn("All colors", response.text)

    def test_part_detail_with_color_id(self):
        response = self.client.get("/lego/part/2345/1/")

        self.assertEqual(response.status_code, 200)
        self.assertParts(
            response.text,
            "Lego Part 2345 Brick 2 x 4, Red",
            "All colors",
            "Included in:",
            "1x in", "111-1 Airport",
        )
        self.assertParts(response.text, "1x in", "123-1 Brick House")

    def test_part_detail_not_found_by_lego_id(self):
        response = self.client.get("/lego/part/999/")

        self.assertEqual(response.status_code, 404)

    def test_part_detail_not_found_by_lego_id_with_valid_color_id(self):
        response = self.client.get("/lego/part/999/1/")

        self.assertEqual(response.status_code, 404)

    def test_part_detail_not_found_by_color_id(self):
        response = self.client.get("/lego/part/2345/99/")

        self.assertEqual(response.status_code, 404)


@test_settings
class TestResponseQuerySet(TestCase):
    fixtures = ["test_data"]

    def test_parts_found_by_num_code(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "2345", "mode": "id"}
        )

        self.assertQuerySetEqual(
            response.context["parts"],
            (("2345", "Red"), ("2345pr0001", "Red"), ("2345", "White")),
            transform=attrgetter("shape.lego_id", "color.name"),
            ordered=False,
        )


@test_settings
class TestSearch(TestCase, OrderedPartsMixin):
    fixtures = ["test_data"]

    def test_set_found_by_name(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "house", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'house'", response.text)
        self.assertParts(response.text, "123-1 Brick House")

    def test_parts_found_by_name(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "plate", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'plate'", response.text)
        self.assertParts(response.text, "23456 Plate 1 x 3, White")
        self.assertParts(response.text, "23456 Plate 1 x 3, Red")

    def test_set_and_parts_found_by_name(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "brick", "mode": "all"}
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
            "/lego/search/", query_params={"q": "123", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for '123'", response.text)
        self.assertParts(response.text, "123-1 Brick House")

    def test_parts_found_by_num_code(self):
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
            "/lego/search/", query_params={"q": "red", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'red'", response.text)
        self.assertParts(response.text, "2345 Brick 2 x 4, Red")
        self.assertParts(response.text, "2345pr0001 Brick 2 x 4 with print, Red")
        self.assertParts(response.text, "23456 Plate 1 x 3, Red")

    def test_set_found_by_name_in_name_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "house", "mode": "name"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'house'", response.text)
        self.assertParts(response.text, "123-1 Brick House")

    def test_set_found_by_lego_id_in_id_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "123", "mode": "id"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for '123'", response.text)
        self.assertParts(response.text, "123-1 Brick House")

    def test_parts_found_by_num_code_in_id_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "2345", "mode": "id"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for '2345'", response.text)
        self.assertParts(response.text, "2345 Brick 2 x 4, Red")
        self.assertParts(response.text, "2345 Brick 2 x 4, White")
        self.assertParts(response.text, "2345pr0001 Brick 2 x 4 with print, Red")
        self.assertNotIn("23456", response.text)

    def test_parts_found_by_color_in_color_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "red", "mode": "color"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("Search Results for 'red'", response.text)
        self.assertParts(response.text, "2345 Brick 2 x 4, Red")
        self.assertParts(response.text, "2345pr0001 Brick 2 x 4 with print, Red")
        self.assertParts(response.text, "23456 Plate 1 x 3, Red")

    def test_nothing_found_by_lego_id_in_name_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "123", "mode": "name"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nothing Found", response.text)

    def test_nothing_found_by_name_in_id_mode(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "brick", "mode": "id"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nothing Found", response.text)

    def test_nothing_found(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "999", "mode": "all"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nothing Found", response.text)


@test_settings
class TestImageUrls(TestCase, OrderedPartsMixin):
    fixtures = ["test_data"]

    def test_set_image_urls(self):
        response = self.client.get("/lego/")

        self.assertEqual(response.status_code, 200)
        # 111-1 has external image URL
        self.assertParts(response.text, "111-1", "test://cdn.test/img/111.jpg")
        # 123-1 has local static file
        self.assertParts(response.text, "123-1", "/img/sets/1.jpg")

    def test_part_image_urls(self):
        response = self.client.get(
            "/lego/search/", query_params={"q": "23456", "mode": "id"}
        )

        self.assertEqual(response.status_code, 200)
        # 23456 White has external image URL
        self.assertParts(
            response.text, "23456", "White", "test://cdn.test/img/23456W.jpg",
        )
        # 23456 Red has no image
        self.assertParts(response.text, "23456", "Red")
        self.assertNotIn("23456R", response.text)
        self.assertNotIn("img/parts", response.text)


@test_settings
class TestAddSet(TestCase, OrderedPartsMixin):
    fixtures = ["test_data", "test_user"]

    @tag("write-db")
    def test_add_set(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "1234-1"}, follow=True
            )
            mock_1.assert_called_once_with("1234-1")
            mock_2.assert_called_once_with("1234-1")

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/set/1234-1/")
        self.assertParts(
            response.text,
            "Lego Set 1234-1 Fighter Jet",
            "Contains:",
            "1x", "fig-0006 Pilot, Blue Helmet",
        )
        self.assertParts(response.text, "2x", "2345 Brick 2 x 4 new, White")
        self.assertParts(response.text, "1x", "2345 Brick 2 x 4 new, Blue")
        self.assertParts(response.text, "1x", "6868 Jet Engine, Blue")
        self.assertParts(response.text, "1x", "23456 Plate 1 x 3, White")
        self.assertParts(response.text, "3x", "4242 Wheel, Black")

    @tag("write-db")
    def test_add_set_without_suffix(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "1122"}, follow=True
            )
            mock_1.assert_called_once_with("1122-1")
            mock_2.assert_called_once_with("1122-1")

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/set/1122-1/")

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
            "/lego/set/add/", data={"set_lego_id": "1234-1"}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/lego/login/?next=/lego/set/add/")


@test_settings
class TestAuth(TestCase, OrderedPartsMixin):
    fixtures = ["test_user"]

    @tag("login")
    def test_login_and_logout(self):
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
