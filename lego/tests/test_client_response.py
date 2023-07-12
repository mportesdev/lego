from django.test import TestCase


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
            b".*1x.*234pr.*Brick 2 x 4",
        )

    def test_set_detail_not_found(self):
        response = self.client.get("/lego/set/999/")

        self.assertEqual(response.status_code, 404)

    def test_part_detail(self):
        response = self.client.get("/lego/part/234pr/")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Lego Part 234pr Brick 2 x 4"
            b".*Included in:"
            b".*1x in.*123-1.*Brick House",
        )

    def test_part_detail_not_found(self):
        response = self.client.get("/lego/part/999/")

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
            b".*234pr.*Brick 2 x 4",
        )

    def test_multiple_results_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "brick", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*brick"
            b".*123-1.*Brick House"
            b".*234pr.*Brick 2 x 4",
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
            b".*234pr.*Brick 2 x 4",
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

    def test_nothing_found_by_lego_id_in_name_mode(self):
        response = self.client.get("/lego/search/", data={"q": "123", "mode": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)

    def test_nothing_found_by_name_in_id_mode(self):
        response = self.client.get("/lego/search/", data={"q": "brick", "mode": "id"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)

    def test_nothing_found(self):
        response = self.client.get("/lego/search/", data={"q": "999", "mode": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)
