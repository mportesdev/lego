import os
import shutil
from pathlib import Path
from tempfile import mkdtemp
import unittest

from django.test import LiveServerTestCase
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from . import get_set_info_mock, get_set_parts_mock


@unittest.skipIf(os.getenv("CI"), reason="Browser tests not run in CI")
class TestBrowserUI(LiveServerTestCase):
    fixtures = ["test_data", "test_user"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ["TMPDIR"] = cls.temp_dir = mkdtemp(dir=Path(__file__).parent)
        cls.addClassCleanup(shutil.rmtree, cls.temp_dir)
        cls.driver = Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.driver.get(f"{self.live_server_url}/lego/")

    def login_test_user(self):
        self.driver.find_element(By.XPATH, "//a[text()='Log in']").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()

    def test_detail_pages(self):
        # go to set detail
        self.driver.find_element(By.XPATH, "//a[text()='123-1']").click()
        self.assertEqual(self.driver.title, "Lego Set 123-1 Brick House")
        self.driver.find_element(By.XPATH, "//img[@src='img123-1.jpg']")
        link = self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")
        self.driver.find_element(By.XPATH, "//div[text()='Red']")
        self.driver.find_element(By.XPATH, "//img[@src='img234prR.jpg']")
        self.driver.find_element(By.XPATH, "//a[text()='567']")
        self.driver.find_element(By.XPATH, "//div[text()='Figure']")
        self.driver.find_element(By.XPATH, "//img[@src='img567.jpg']")

        # go to part detail
        link.click()
        self.assertEqual(self.driver.title, "Lego Part 234pr Brick 2 x 4, Red")
        self.driver.find_element(By.XPATH, "//img[@src='img234prR.jpg']")
        self.driver.find_element(By.XPATH, "//a[text()='123-1']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick House']")
        self.driver.find_element(By.XPATH, "//img[@src='img123-1.jpg']")

        # go to index page
        self.driver.find_element(By.ID, "index_link").click()
        self.assertEqual(self.driver.title, "Our Lego")
        self.driver.find_element(By.XPATH, "//a[text()='123-1']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick House']")
        self.driver.find_element(By.XPATH, "//img[@src='img123-1.jpg']")

    def test_search(self):
        # search everywhere
        self.driver.find_element(By.ID, "id_q").send_keys("brick")
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for 'brick'")
        self.driver.find_element(By.XPATH, "//a[text()='123-1']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick House']")
        self.driver.find_element(By.XPATH, "//img[@src='img123-1.jpg']")
        self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")
        self.driver.find_element(By.XPATH, "//div[text()='Red']")
        self.driver.find_element(By.XPATH, "//img[@src='img234prR.jpg']")
        self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")
        self.driver.find_element(By.XPATH, "//div[text()='White']")
        self.driver.find_element(By.XPATH, "//img[@src='img234prW.jpg']")

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
        self.driver.find_element(By.XPATH, "//img[@src='img123-1.jpg']")

        # search by lego_id
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("234")
        self.driver.find_element(By.ID, "id_mode_2").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for '234'")
        self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")
        self.driver.find_element(By.XPATH, "//div[text()='Red']")
        self.driver.find_element(By.XPATH, "//img[@src='img234prR.jpg']")
        self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")
        self.driver.find_element(By.XPATH, "//div[text()='White']")
        self.driver.find_element(By.XPATH, "//img[@src='img234prW.jpg']")

        # search by color
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("red")
        self.driver.find_element(By.ID, "id_mode_3").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for 'red'")
        self.driver.find_element(By.XPATH, "//a[text()='234pr']")
        self.driver.find_element(By.XPATH, "//div[text()='Brick 2 x 4']")
        self.driver.find_element(By.XPATH, "//div[text()='Red']")

    def test_search_form_populated_from_get(self):
        self.driver.find_element(By.ID, "id_q").send_keys("123")
        self.driver.find_element(By.ID, "id_mode_2").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(
            self.driver.find_element(By.ID, "id_q").get_attribute("value"),
            "123",
        )
        self.assertTrue(self.driver.find_element(By.ID, "id_mode_2").is_selected())

    def test_add_set(self):
        self.login_test_user()
        self.driver.find_element(By.XPATH, "//a[text()='Add a New Lego Set']").click()
        self.assertEqual(self.driver.title, "Add a New Lego Set")

        with (
            get_set_info_mock(),
            get_set_parts_mock(),
            self.assertLogs("lego.views", "INFO"),
        ):
            self.driver.find_element(By.ID, "id_set_lego_id").send_keys("1234-1")
            self.driver.find_element(By.ID, "add_set_submit").click()

        self.assertEqual(self.driver.title, "Lego Set 1234-1 Fighter Jet")
        self.driver.find_element(By.XPATH, "//img[@src='img1234-1.jpg']")
        self.driver.find_element(By.XPATH, "//a[text()='333']")
        self.driver.find_element(By.XPATH, "//div[text()='Pilot']")
        self.driver.find_element(By.XPATH, "//img[@src='img333.jpg']")
        self.driver.find_element(By.XPATH, "//a[text()='111']")
        self.driver.find_element(By.XPATH, "//div[text()='Jet Engine']")
        self.driver.find_element(By.XPATH, "//div[text()='Blue']")
        self.driver.find_element(By.XPATH, "//img[@src='img111b.jpg']")
        self.driver.find_element(By.XPATH, "//a[text()='222']")
        self.driver.find_element(By.XPATH, "//div[text()='Wheel']")
        self.driver.find_element(By.XPATH, "//div[text()='Black']")
        self.driver.find_element(By.XPATH, "//img[@src='img222k.jpg']")

    def test_add_set_without_suffix(self):
        self.login_test_user()
        self.driver.find_element(By.XPATH, "//a[text()='Add a New Lego Set']").click()
        self.assertEqual(self.driver.title, "Add a New Lego Set")

        with (
            get_set_info_mock(),
            get_set_parts_mock(),
            self.assertLogs("lego.views", "INFO"),
        ):
            self.driver.find_element(By.ID, "id_set_lego_id").send_keys("1234")
            self.driver.find_element(By.ID, "add_set_submit").click()

        self.assertTrue(self.driver.current_url.endswith("/lego/set/1234-1/"))
        self.assertEqual(self.driver.title, "Lego Set 1234-1 Fighter Jet")

    def test_login_and_logout(self):
        # log in
        self.driver.find_element(By.XPATH, "//a[text()='Log in']").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()
        # log out
        self.driver.find_element(By.XPATH, "//div[text()='test-user']")
        self.driver.find_element(By.XPATH, "//a[text()='Admin Page']")
        self.driver.find_element(By.ID, "log_out").click()
        self.driver.find_element(By.XPATH, "//a[text()='Log in']")

    def test_login_redirects_to_referer(self):
        # go to set detail page
        self.driver.find_element(By.XPATH, "//a[text()='123-1']").click()

        # log in
        self.driver.find_element(By.XPATH, "//a[text()='Log in']").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()

        # redirected back to set detail page
        self.assertTrue(self.driver.current_url.endswith("/lego/set/123-1/"))

    def test_login_redirects_to_index_if_referer_is_missing(self):
        # go directly to login page
        self.driver.get(f"{self.live_server_url}/lego/login/")

        # log in
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()

        # redirected to index page
        self.assertTrue(self.driver.current_url.endswith("/lego/"))
