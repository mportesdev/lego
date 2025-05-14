import os
import shutil
from pathlib import Path
from tempfile import mkdtemp

from django.contrib.staticfiles.testing import LiveServerTestCase
from django.test import tag
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from . import test_settings, get_set_info_mock, get_set_parts_mock


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

    def test_index_and_detail_pages(self):
        self.assertIn("Home", self.driver.title)
        set_link = self.driver.find_element(By.LINK_TEXT, "123-1")

        # go to set detail
        set_link.click()
        self.assertIn("Lego Set 123-1 Brick House", self.driver.title)
        part_link = self.driver.find_element(By.LINK_TEXT, "2345")
        self.driver.find_element(By.LINK_TEXT, "fig-0008")
        self.driver.find_element(By.LINK_TEXT, "2345pr0001")

        # go to part detail
        part_link.click()
        self.assertIn("Lego Part 2345 Brick 2 x 4, Red", self.driver.title)
        set_link = self.driver.find_element(By.LINK_TEXT, "123-1")

        # go back to set detail
        set_link.click()
        self.assertIn("Lego Set 123-1 Brick House", self.driver.title)
        home_link = self.driver.find_element(By.LINK_TEXT, "O&F Lego")

        # go back to index page
        home_link.click()
        self.assertIn("Home", self.driver.title)

    def test_search(self):
        # search everywhere
        self.driver.find_element(By.ID, "id_q").send_keys("brick")
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertIn("Search Results for 'brick'", self.driver.title)
        self.driver.find_element(By.LINK_TEXT, "123-1")
        self.driver.find_element(By.LINK_TEXT, "2345")
        self.driver.find_element(By.LINK_TEXT, "2345pr0001")

        # search in names
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("house")
        self.driver.find_element(By.ID, "id_mode_1").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertIn("Search Results for 'house'", self.driver.title)
        self.driver.find_element(By.LINK_TEXT, "123-1")

        # search in lego IDs
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("2345")
        self.driver.find_element(By.ID, "id_mode_2").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertIn("Search Results for '2345'", self.driver.title)
        self.driver.find_element(By.LINK_TEXT, "2345")
        self.driver.find_element(By.LINK_TEXT, "23456")
        self.driver.find_element(By.LINK_TEXT, "2345pr0001")

        # search in colors
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("white")
        self.driver.find_element(By.ID, "id_mode_3").click()
        self.driver.find_element(By.ID, "search_submit").click()

        self.assertIn("Search Results for 'white'", self.driver.title)
        self.driver.find_element(By.LINK_TEXT, "2345")
        self.driver.find_element(By.LINK_TEXT, "23456")

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
        # log in
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()

        # attempt to add existing set
        self.driver.find_element(By.LINK_TEXT, "Add a New Lego Set").click()
        self.driver.find_element(By.ID, "id_set_lego_id").send_keys("123")
        with get_set_info_mock(), get_set_parts_mock():
            self.driver.find_element(By.ID, "add_set_submit").click()

        # nothing was added
        self.assertIn("Add a New Lego Set", self.driver.title)
        self.assertTrue(self.driver.current_url.endswith("/set/add/"))

        # attempt to add invalid set
        self.driver.find_element(By.LINK_TEXT, "Add a New Lego Set").click()
        self.driver.find_element(By.ID, "id_set_lego_id").send_keys("999")
        with get_set_info_mock(), get_set_parts_mock():
            self.driver.find_element(By.ID, "add_set_submit").click()

        # nothing was added
        self.assertIn("Add a New Lego Set", self.driver.title)
        self.assertTrue(self.driver.current_url.endswith("/set/add/"))

        # add a new set
        self.driver.find_element(By.LINK_TEXT, "Add a New Lego Set").click()
        self.driver.find_element(By.ID, "id_set_lego_id").send_keys("1234")
        with get_set_info_mock(), get_set_parts_mock():
            self.driver.find_element(By.ID, "add_set_submit").click()

        self.assertIn("Lego Set 1234-1 Fighter Jet", self.driver.title)
        self.assertTrue(self.driver.current_url.endswith("/set/1234-1/"))
        self.driver.find_element(By.LINK_TEXT, "2345")
        self.driver.find_element(By.LINK_TEXT, "6868")
        self.driver.find_element(By.LINK_TEXT, "fig-0006")
        self.driver.find_element(By.LINK_TEXT, "23456")
        self.driver.find_element(By.LINK_TEXT, "4242")

    @tag("login")
    def test_login_and_logout(self):
        # log in
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        self.driver.find_element(By.ID, "id_password").send_keys("test-password")
        self.driver.find_element(By.ID, "login_submit").click()
        self.driver.find_element(By.XPATH, "//div[text()='test-user']")
        logout_link = self.driver.find_element(By.ID, "log_out")
        self.driver.find_element(By.LINK_TEXT, "Admin Page")

        # log out
        logout_link.click()
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
