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
