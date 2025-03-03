import re

from django.test import TestCase

from . import test_settings, get_set_info_mock, get_set_parts_mock


@test_settings
class TestGetResponse(TestCase):
    fixtures = ["test_data"]

    def test_index_page(self):
        response = self.client.get("/lego/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Latest Additions",
                "111-1", "Airport", "test://cdn.test/img/111.jpg",
                "123-1", "Brick House", "/img/sets/1.jpg",
            ),
        )

    def test_set_detail(self):
        response = self.client.get("/lego/set/123-1/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Lego Set 123-1 Brick House", "/img/sets/1.jpg",
                "Contains:",
                "1x", "234pr", "Brick 2 x 4", "Red", "/img/parts/1.jpg",
                "1x", "567", "Figure", "/img/parts/3.jpg",
            ),
        )

    def test_set_detail_not_found(self):
        response = self.client.get("/lego/set/999/")

        self.assertEqual(response.status_code, 404)

    def test_part_detail(self):
        response = self.client.get("/lego/part/567/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Lego Part 567 Figure", "/img/parts/3.jpg",
                "Included in:",
                "1x in", "123-1", "Brick House", "/img/sets/1.jpg",
            ),
        )

    def test_part_detail_with_color_id(self):
        response = self.client.get("/lego/part/234pr/1/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Lego Part 234pr Brick 2 x 4, Red", "/img/parts/1.jpg",
                "Included in:",
                "1x in", "123-1", "Brick House", "/img/sets/1.jpg",
             ),
        )

    def test_part_detail_not_found_if_lego_id_invalid(self):
        response = self.client.get("/lego/part/999/")

        self.assertEqual(response.status_code, 404)

    def test_part_detail_not_found_if_lego_id_invalid_with_color_id(self):
        response = self.client.get("/lego/part/999/1/")

        self.assertEqual(response.status_code, 404)

    def test_part_detail_not_found_if_color_id_invalid(self):
        response = self.client.get("/lego/part/234pr/99/")

        self.assertEqual(response.status_code, 404)


@test_settings
class TestSearch(TestCase):
    fixtures = ["test_data"]

    def test_set_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "house", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "house",
                "123-1", "Brick House", "/img/sets/1.jpg",
            ),
        )

    def test_part_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "2 x 4", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "2 x 4",
                "234pr", "Brick 2 x 4", "Red", "/img/parts/1.jpg",
                "234pr", "Brick 2 x 4", "White", "/img/parts/2.jpg",
            ),
        )

    def test_multiple_results_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "brick", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "brick",
                "123-1", "Brick House", "/img/sets/1.jpg",
                "234pr", "Brick 2 x 4", "Red", "/img/parts/1.jpg",
                "234pr", "Brick 2 x 4", "White", "/img/parts/2.jpg",
            ),
        )

    def test_set_found_by_lego_id(self):
        response = self.client.get("/lego/search/", data={"q": "123", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "123",
                "123-1", "Brick House", "/img/sets/1.jpg",
            ),
        )

    def test_part_found_by_lego_id(self):
        response = self.client.get("/lego/search/", data={"q": "234", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "234",
                "234pr", "Brick 2 x 4", "Red", "/img/parts/1.jpg",
                "234pr", "Brick 2 x 4", "White", "/img/parts/2.jpg",
            ),
        )

    def test_part_found_by_color(self):
        response = self.client.get("/lego/search/", data={"q": "red", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "red",
                "234pr", "Brick 2 x 4", "Red",
            ),
        )

    def test_set_found_by_name_in_name_mode(self):
        response = self.client.get("/lego/search/", data={"q": "house", "mode": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "house",
                "123-1", "Brick House",
            ),
        )

    def test_set_found_by_lego_id_in_id_mode(self):
        response = self.client.get("/lego/search/", data={"q": "123", "mode": "id"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "123",
                "123-1", "Brick House",
             ),
        )

    def test_part_found_by_color_in_color_mode(self):
        response = self.client.get("/lego/search/", data={"q": "red", "mode": "color"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Search Results for", "red",
                "234pr", "Brick 2 x 4", "Red",
            ),
        )

    def test_nothing_found_by_lego_id_in_name_mode(self):
        response = self.client.get("/lego/search/", data={"q": "123", "mode": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)

    def test_nothing_found_by_color_in_name_mode(self):
        response = self.client.get("/lego/search/", data={"q": "red", "mode": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)

    def test_nothing_found_by_name_in_id_mode(self):
        response = self.client.get("/lego/search/", data={"q": "brick", "mode": "id"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)

    def test_nothing_found_by_color_in_id_mode(self):
        response = self.client.get("/lego/search/", data={"q": "red", "mode": "id"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)

    def test_nothing_found_by_name_in_color_mode(self):
        response = self.client.get("/lego/search/", data={"q": "brick", "mode": "color"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)

    def test_nothing_found_by_lego_id_in_color_mode(self):
        response = self.client.get("/lego/search/", data={"q": "123", "mode": "color"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)

    def test_nothing_found(self):
        response = self.client.get("/lego/search/", data={"q": "999", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)


class TestAddSet(TestCase):
    fixtures = ["test_data", "test_user"]

    def test_add_set(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            with self.assertLogs("lego.views", "INFO"):
                response = self.client.post(
                    "/lego/set/add/", data={"set_lego_id": "1234-1"}, follow=True
                )
            mock_1.assert_called_once_with("1234-1")
            mock_2.assert_called_once_with("1234-1")

        self.assertRedirects(response, "/lego/set/1234-1/")
        self.assertRegex(
            response.content.decode(),
            _ordered_regex(
                "Lego Set 1234-1 Fighter Jet", "test://cdn.test/img/1234.jpg",
                "Contains:",
                "1x", "234pr", "Brick 2 x 4 with studs", "Blue", "test://cdn.test/img/234prB.jpg",
                "2x", "111", "Jet Engine", "Blue", "test://cdn.test/img/111b.jpg",
                "1x", "333", "Pilot", "test://cdn.test/img/333.jpg",
                "1x", "102", "Plate 1 x 3", "White", "test://cdn.test/img/102W2.jpg",
                "3x", "222", "Wheel", "Black",
            ),
        )

    def test_add_set_without_suffix(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            with self.assertLogs("lego.views", "INFO"):
                response = self.client.post(
                    "/lego/set/add/", data={"set_lego_id": "1234"}, follow=True
                )
            mock_1.assert_called_once_with("1234-1")
            mock_2.assert_called_once_with("1234-1")

        self.assertRedirects(response, "/lego/set/1234-1/")

    def test_add_set_existing_lego_id(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            with self.assertLogs("lego.views", "WARNING"):
                response = self.client.post(
                    "/lego/set/add/", data={"set_lego_id": "123-1"}, follow=True
                )
            mock_1.assert_not_called()
            mock_2.assert_not_called()

        self.assertRedirects(response, "/lego/set/add/")

    def test_add_set_existing_lego_id_without_suffix(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            with self.assertLogs("lego.views", "WARNING"):
                response = self.client.post(
                    "/lego/set/add/", data={"set_lego_id": "123"}, follow=True
                )
            mock_1.assert_not_called()
            mock_2.assert_not_called()

        self.assertRedirects(response, "/lego/set/add/")

    def test_add_set_invalid_lego_id(self):
        self.client.login(username="test-user", password="test-password")
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            with self.assertLogs("lego.views", "ERROR"):
                response = self.client.post(
                    "/lego/set/add/", data={"set_lego_id": "999-1"}, follow=True
                )
            mock_1.assert_called_once_with("999-1")
            mock_2.assert_not_called()

        self.assertRedirects(response, "/lego/set/add/")

    def test_add_set_redirects_to_login_if_not_logged_in(self):
        response = self.client.post(
            "/lego/set/add/", data={"set_lego_id": "1234-1"}, follow=True
        )
        self.assertRedirects(response, "/lego/login/?next=/lego/set/add/")


class TestAuth(TestCase):
    fixtures = ["test_user"]

    def test_login_and_logout(self):
        response = self.client.get("/lego/")
        self.assertIn(b"Log in", response.content)
        self.assertNotIn(b"Add a New Lego Set", response.content)
        self.assertNotIn(b"Admin Page", response.content)

        # log in
        response = self.client.post(
            "/lego/login/",
            data={"username": "test-user", "password": "test-password"},
            follow=True,
        )
        self.assertRedirects(response, "/lego/")
        self.assertRegex(
            response.content.decode(),
            _ordered_regex("test-user", "Log out"),
        )
        self.assertIn(b"Add a New Lego Set", response.content)
        self.assertIn(b"Admin Page", response.content)

        # log out
        response = self.client.post("/lego/logout/", follow=True)
        self.assertRedirects(response, "/lego/")
        self.assertIn(b"Log in", response.content)
        self.assertNotIn(b"Add a New Lego Set", response.content)
        self.assertNotIn(b"Admin Page", response.content)


def _ordered_regex(*parts):
    return re.compile(
        ".*?".join(re.escape(part) for part in parts),
        flags=re.DOTALL,
    )
