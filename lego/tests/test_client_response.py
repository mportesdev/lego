from django.test import TestCase

from . import get_set_info_mock, get_set_parts_mock


class TestGetResponse(TestCase):
    fixtures = ["test_data"]

    def test_index_page(self):
        response = self.client.get("/lego/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)<title>Our Lego</title>"
            b".*Our Lego"
            b".*All Sets"
            b".*123-1.*Brick House",
        )

    def test_set_detail(self):
        response = self.client.get("/lego/set/123-1/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Lego Set 123-1 Brick House"
            b".*Contains:"
            b".*1x.*234pr.*Brick 2 x 4.*Red",
            b".*1x.*567.*Figure",
        )

    def test_set_detail_not_found(self):
        response = self.client.get("/lego/set/999/")

        self.assertEqual(response.status_code, 404)

    def test_part_detail(self):
        response = self.client.get("/lego/part/567/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Lego Part 567 Figure"
            b".*Included in:"
            b".*1x in.*123-1.*Brick House",
        )

    def test_part_detail_with_color_id(self):
        response = self.client.get("/lego/part/234pr/1/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Lego Part 234pr Brick 2 x 4, Red"
            b".*Included in:"
            b".*1x in.*123-1.*Brick House",
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


class TestSearch(TestCase):
    fixtures = ["test_data"]

    def test_set_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "house", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*house"
            b".*123-1.*Brick House",
        )

    def test_part_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "2 x 4", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*2 x 4"
            b".*234pr.*Brick 2 x 4.*Red",
            b".*234pr.*Brick 2 x 4.*White",
        )

    def test_multiple_results_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "brick", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*brick"
            b".*123-1.*Brick House"
            b".*234pr.*Brick 2 x 4.*Red",
            b".*234pr.*Brick 2 x 4.*White",
        )

    def test_set_found_by_lego_id(self):
        response = self.client.get("/lego/search/", data={"q": "123", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*123"
            b".*123-1.*Brick House",
        )

    def test_part_found_by_lego_id(self):
        response = self.client.get("/lego/search/", data={"q": "234", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*234"
            b".*234pr.*Brick 2 x 4.*Red",
            b".*234pr.*Brick 2 x 4.*White",
        )

    def test_part_found_by_color(self):
        response = self.client.get("/lego/search/", data={"q": "red", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*red"
            b".*234pr.*Brick 2 x 4.*Red",
        )

    def test_set_found_by_name_in_name_mode(self):
        response = self.client.get("/lego/search/", data={"q": "house", "mode": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*house"
            b".*123-1.*Brick House",
        )

    def test_set_found_by_lego_id_in_id_mode(self):
        response = self.client.get("/lego/search/", data={"q": "123", "mode": "id"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*123"
            b".*123-1.*Brick House",
        )

    def test_part_found_by_color_in_color_mode(self):
        response = self.client.get("/lego/search/", data={"q": "red", "mode": "color"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*red"
            b".*234pr.*Brick 2 x 4.*Red",
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
    fixtures = ["test_data"]

    def test_add_set(self):
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "1234-1"}, follow=True
            )
            mock_1.assert_called_once_with("1234-1")
            mock_2.assert_called_once_with("1234-1")

        self.assertRedirects(response, "/lego/set/1234-1/")
        self.assertRegex(
            response.content,
            b"(?s)Lego Set 1234-1 Fighter Jet"
            b".*Contains:"
            b".*1x.*111.*Jet Engine.*Blue"
            b".*3x.*222.*Wheel.*Black",
        )

    def test_add_set_existing_lego_id(self):
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "123-1"}, follow=True
            )
            mock_1.assert_not_called()
            mock_2.assert_not_called()

        self.assertRedirects(response, "/lego/")

    def test_add_set_invalid_lego_id(self):
        with get_set_info_mock() as mock_1, get_set_parts_mock() as mock_2:
            response = self.client.post(
                "/lego/set/add/", data={"set_lego_id": "999-1"}, follow=True
            )
            mock_1.assert_called_once_with("999-1")
            mock_2.assert_not_called()

        self.assertRedirects(response, "/lego/")
