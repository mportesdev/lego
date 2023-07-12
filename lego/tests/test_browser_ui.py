import os
import shutil
from pathlib import Path
from tempfile import mkdtemp

from django.test import LiveServerTestCase
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from lego.models import LegoPart, LegoSet


class TestBrowserUI(LiveServerTestCase):
    def setUp(self):
        house = LegoSet.objects.create(lego_id="123-1", name="Brick House")
        brick = LegoPart.objects.create(lego_id="234pr", name="Brick 2 x 4")
        house.parts.add(brick)

        self.temp_dir = mkdtemp(dir=Path(__file__).parent)
        os.environ["TMPDIR"] = self.temp_dir
        self.driver = Firefox()
        self.driver.get(f"{self.live_server_url}/lego/")

    def tearDown(self):
        self.driver.quit()
        shutil.rmtree(self.temp_dir)

    def test_detail_pages(self):
        # go to set detail
        self.driver.find_element(By.XPATH, "//a[text()='123-1']").click()
        self.assertEqual(self.driver.title, "Lego Set 123-1 Brick House")
        link = self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")

        # go to part detail
        link.click()
        self.assertEqual(self.driver.title, "Lego Part 234pr Brick 2 x 4")
        self.driver.find_element(By.XPATH, "//a[text()='123-1']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick House']")

        # go to index page
        self.driver.find_element(By.ID, "index_link").click()
        self.assertEqual(self.driver.title, "Our Lego")
        self.driver.find_element(By.XPATH, "//a[text()='123-1']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick House']")

    def test_search(self):
        # search everywhere
        self.driver.find_element(By.ID, "id_q").send_keys("brick")
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for 'brick'")
        self.driver.find_element(By.XPATH, "//a[text()='123-1']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick House']")
        self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")

        self.driver.find_element(By.ID, "id_q").send_keys("99")
        self.driver.find_element(By.ID, "search_submit").click()
        self.driver.find_element(By.XPATH, "//div[text()='Nothing Found']")

        # search by name
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("house")
        self.driver.find_element(By.ID, "id_mode_1").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for 'house'")
        self.driver.find_element(By.XPATH, "//a[text()='123-1']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick House']")

        # search by lego_id
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("234")
        self.driver.find_element(By.ID, "id_mode_2").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for '234'")
        self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")

    def test_search_form_populated_from_get(self):
        self.driver.find_element(By.ID, "id_q").send_keys("123")
        self.driver.find_element(By.ID, "id_mode_2").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(
            self.driver.find_element(By.ID, "id_q").get_attribute("value"),
            "123",
        )
        self.assertTrue(self.driver.find_element(By.ID, "id_mode_2").is_selected())
