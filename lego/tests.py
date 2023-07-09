from django.test import TestCase

from lego.models import LegoPart, LegoSet


class TestGetResponse(TestCase):
    @classmethod
    def setUpTestData(cls):
        house = LegoSet.objects.create(lego_id="123-1", name="Brick House")
        brick = LegoPart.objects.create(lego_id="234pr", name="Brick 2 x 4")
        house.parts.add(brick)

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
    @classmethod
    def setUpTestData(cls):
        LegoSet.objects.create(lego_id="123-1", name="Brick House")
        LegoPart.objects.create(lego_id="234pr", name="Brick 2 x 4")

    def test_set_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "house"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*house"
            b".*123-1.*Brick House",
        )

    def test_part_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "2 x 4"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*2 x 4"
            b".*234pr.*Brick 2 x 4",
        )

    def test_multiple_results_found_by_name(self):
        response = self.client.get("/lego/search/", data={"q": "brick"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*brick"
            b".*123-1.*Brick House"
            b".*234pr.*Brick 2 x 4",
        )

    def test_set_found_by_lego_id(self):
        response = self.client.get("/lego/search/", data={"q": "123"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*123"
            b".*123-1.*Brick House",
        )

    def test_part_found_by_lego_id(self):
        response = self.client.get("/lego/search/", data={"q": "234"})

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content,
            b"(?s)Search Results for.*234"
            b".*234pr.*Brick 2 x 4",
        )

    def test_nothing_found(self):
        response = self.client.get("/lego/search/", data={"q": "999"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nothing Found", response.content)
