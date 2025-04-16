import os
import shutil
from pathlib import Path
from tempfile import mkdtemp
import unittest

from django.contrib.staticfiles.testing import LiveServerTestCase
from django.test import tag
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from . import test_settings, get_set_info_mock, get_set_parts_mock


@unittest.skipIf(os.getenv("CI"), reason="Browser tests not run in CI")
@tag("browser")
@test_settings
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

    def test_index_and_detail_pages(self):
        self.assertEqual(self.driver.title, "Home | O&F Lego")

        # go to set detail
        self.driver.find_element(By.LINK_TEXT, "123-1").click()
        self.assertEqual(self.driver.title, "Lego Set 123-1 Brick House | O&F Lego")
        link = self.driver.find_element(By.LINK_TEXT, "234pr")
        self.driver.find_element(By.LINK_TEXT, "567")

        # go to part detail
        link.click()
        self.assertEqual(self.driver.title, "Lego Part 234pr Brick 2 x 4, Red | O&F Lego")

        # go back to set detail
        self.driver.find_element(By.LINK_TEXT, "123-1").click()
        self.assertEqual(self.driver.title, "Lego Set 123-1 Brick House | O&F Lego")

        # go back to index page
        self.driver.find_element(By.LINK_TEXT, "O&F Lego").click()
        self.assertEqual(self.driver.title, "Home | O&F Lego")

    def test_search(self):
        # search everywhere
        self.driver.find_element(By.ID, "id_q").send_keys("brick")
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for 'brick' | O&F Lego")
        self.driver.find_element(By.LINK_TEXT, "123-1")
        self.driver.find_element(By.LINK_TEXT, "234pr")

        # search by name
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("house")
        self.driver.find_element(By.ID, "id_mode_1").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for 'house' | O&F Lego")
        self.driver.find_element(By.LINK_TEXT, "123-1")

        # search by lego_id
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("234")
        self.driver.find_element(By.ID, "id_mode_2").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for '234' | O&F Lego")
        self.driver.find_element(By.LINK_TEXT, "234pr")

        # search by color
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("red")
        self.driver.find_element(By.ID, "id_mode_3").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(self.driver.title, "Search Results for 'red' | O&F Lego")
        self.driver.find_element(By.LINK_TEXT, "234pr")

    def test_search_form_populated_from_get(self):
        self.driver.find_element(By.ID, "id_q").send_keys("123")
        self.driver.find_element(By.ID, "id_mode_2").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertEqual(
            self.driver.find_element(By.ID, "id_q").get_attribute("value"),
            "123",
        )
        self.assertTrue(self.driver.find_element(By.ID, "id_mode_2").is_selected())

    @tag("write-db")
    def test_add_set(self):
        self.login_test_user()
        self.driver.find_element(By.LINK_TEXT, "Add a New Lego Set").click()
        self.assertEqual(self.driver.title, "Add a New Lego Set | O&F Lego")

        with (
            get_set_info_mock(),
            get_set_parts_mock(),
            self.assertLogs("lego.views", "INFO"),
        ):
            self.driver.find_element(By.ID, "id_set_lego_id").send_keys("1234-1")
            self.driver.find_element(By.ID, "add_set_submit").click()

        self.assertEqual(self.driver.title, "Lego Set 1234-1 Fighter Jet | O&F Lego")
        self.driver.find_element(By.LINK_TEXT, "234pr")
        self.driver.find_element(By.LINK_TEXT, "111")
        self.driver.find_element(By.LINK_TEXT, "333")
        self.driver.find_element(By.LINK_TEXT, "102")
        self.driver.find_element(By.LINK_TEXT, "222")

    @tag("write-db")
    def test_add_set_without_suffix(self):
        self.login_test_user()
        self.driver.find_element(By.LINK_TEXT, "Add a New Lego Set").click()

        with (
            get_set_info_mock(),
            get_set_parts_mock(),
            self.assertLogs("lego.views", "INFO"),
        ):
            self.driver.find_element(By.ID, "id_set_lego_id").send_keys("1234")
            self.driver.find_element(By.ID, "add_set_submit").click()

        self.assertTrue(self.driver.current_url.endswith("/lego/set/1234-1/"))
        self.assertEqual(self.driver.title, "Lego Set 1234-1 Fighter Jet | O&F Lego")

    @tag("login")
    def test_login_and_logout(self):
        # log in
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()
        self.driver.find_element(By.XPATH, "//div[text()='test-user']")
        self.driver.find_element(By.LINK_TEXT, "Admin Page")
        # log out
        self.driver.find_element(By.ID, "log_out").click()
        self.driver.find_element(By.LINK_TEXT, "Log in")

    @tag("login")
    def test_login_redirects_to_referer(self):
        # go to set detail page
        self.driver.find_element(By.LINK_TEXT, "123-1").click()

        # log in
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()

        # redirected back to set detail page
        self.assertTrue(self.driver.current_url.endswith("/lego/set/123-1/"))

    @tag("login")
    def test_login_redirects_to_index_if_referer_is_missing(self):
        # go directly to login page
        self.driver.get(f"{self.live_server_url}/lego/login/")

        # log in
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()

        # redirected to index page
        self.assertTrue(self.driver.current_url.endswith("/lego/"))
