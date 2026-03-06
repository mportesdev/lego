import os
import shutil
from pathlib import Path
from tempfile import mkdtemp

from django.contrib.staticfiles.testing import LiveServerTestCase
from django.test import tag
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

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
        options = Options()
        if not os.getenv("LEGO_TEST_FIREFOX_GUI"):
            options.add_argument("-headless")
        cls.driver = Firefox(options=options)
        cls.driver.implicitly_wait(5)
        cls.wait = WebDriverWait(cls.driver, 5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.driver.get(f"{self.live_server_url}/lego/")

    def test_index_and_detail_pages(self):
        self.assertIn("Home", self.driver.title)
        set_link = self.driver.find_element(By.XPATH, "//a[starts-with(@title, '123-1')]")

        # go to set detail
        set_link.click()
        self.wait.until(EC.title_contains("Lego Set 123-1"))
        part_link = self.driver.find_element(By.XPATH, "//a[starts-with(@title, '2345')]")
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, 'fig-0008')]")
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '2345pr0001')]")

        # go to part detail
        part_link.click()
        self.wait.until(EC.title_contains("Lego Part 2345"))
        colors_link = self.driver.find_element(By.ID, "all_colors")

        # go to colors
        colors_link.click()
        part_link = self.driver.find_element(By.XPATH, "//a[@title='2345 Brick 2 x 4, White']")

        # go to other part detail
        part_link.click()
        set_link = self.driver.find_element(By.XPATH, "//a[starts-with(@title, '111-1')]")

        # go to other set detail
        set_link.click()
        self.wait.until(EC.title_contains("Lego Set 111-1"))
        home_link = self.driver.find_element(By.LINK_TEXT, "O&F Lego")

        # go back to index page
        home_link.click()
        self.wait.until(EC.title_contains("Home"))

    def test_hide_show_in_set_detail(self):
        # go to set detail
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '123-1')]").click()
        item = self.driver.find_element(By.ID, "item_1")
        toggle = self.driver.find_element(By.ID, "hide_show_1")
        # hide
        toggle.click()
        self.assertAlmostEqual(float(item.get_property("style")["opacity"]), 0.25)
        # show
        toggle.click()
        self.assertAlmostEqual(float(item.get_property("style")["opacity"]), 1.0)

    def test_search(self):
        # search everywhere
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.send_keys("brick")
        search_field.submit()

        self.wait.until(EC.title_contains("brick"))
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '123-1')]")
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '2345')]")
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '2345pr0001')]")

        # search in names
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("house")
        self.driver.find_element(By.ID, "id_mode_1").click()
        search_field.submit()

        self.wait.until(EC.title_contains("house"))
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '123-1')]")

        # search in lego IDs
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("2345")
        self.driver.find_element(By.ID, "id_mode_2").click()
        search_field.submit()

        self.wait.until(EC.title_contains("2345"))
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '2345')]")
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '2345pr0001')]")

        # search in colors
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.clear()
        search_field.send_keys("white")
        self.driver.find_element(By.ID, "id_mode_3").click()
        search_field.submit()

        self.wait.until(EC.title_contains("white"))
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '2345')]")
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '23456')]")

    def test_search_form_populated_from_get(self):
        search_field = self.driver.find_element(By.ID, "id_q")
        search_field.send_keys("123")
        self.driver.find_element(By.ID, "id_mode_2").click()
        search_field.submit()

        self.wait.until(EC.title_contains("123"))
        self.assertEqual(
            self.driver.find_element(By.ID, "id_q").get_attribute("value"),
            "123",
        )
        self.assertTrue(self.driver.find_element(By.ID, "id_mode_2").is_selected())

    @tag("log in", "write-db")
    def test_add_set(self):
        # log in
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        input_field = self.driver.find_element(By.ID, "id_password")
        input_field.send_keys("test-password")
        input_field.submit()

        # attempt to add existing set
        self.driver.find_element(By.LINK_TEXT, "Add a New Lego Set").click()
        input_field = self.driver.find_element(By.ID, "id_set_lego_id")
        input_field.send_keys("123")
        with get_set_info_mock(), get_set_parts_mock():
            input_field.submit()
            self.wait.until(EC.staleness_of(input_field))

        # nothing was added
        self.assertEndsWith(self.driver.current_url, "/set/add/")

        # attempt to add invalid set
        input_field = self.driver.find_element(By.ID, "id_set_lego_id")
        input_field.send_keys("999")
        with get_set_info_mock(), get_set_parts_mock():
            input_field.submit()
            self.wait.until(EC.staleness_of(input_field))

        # nothing was added
        self.assertEndsWith(self.driver.current_url, "/set/add/")

        # add a new set
        input_field = self.driver.find_element(By.ID, "id_set_lego_id")
        input_field.send_keys("2001")
        with get_set_info_mock(), get_set_parts_mock():
            input_field.submit()
            self.wait.until(EC.title_contains("Lego Set 2001-1"))

        self.assertEndsWith(self.driver.current_url, "/set/2001-1/")
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '20001')]")

    @tag("login")
    def test_login_and_logout(self):
        # log in
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        input_field = self.driver.find_element(By.ID, "id_password")
        input_field.send_keys("test-password")
        input_field.submit()
        self.wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div"), "test-user")
        )
        logout_link = self.driver.find_element(By.ID, "log_out")
        self.driver.find_element(By.LINK_TEXT, "Admin Page")

        # log out
        logout_link.click()
        self.driver.find_element(By.LINK_TEXT, "Log in")

    @tag("login")
    def test_login_redirects_to_referer(self):
        # go to set detail page
        self.driver.find_element(By.XPATH, "//a[starts-with(@title, '123-1')]").click()
        self.wait.until(EC.title_contains("Lego Set 123-1"))

        # log in
        self.driver.find_element(By.LINK_TEXT, "Log in").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        input_field = self.driver.find_element(By.ID, "id_password")
        input_field.send_keys("test-password")
        input_field.submit()

        # redirected back to set detail page
        self.wait.until(EC.title_contains("Lego Set 123-1"))
        self.assertEndsWith(self.driver.current_url, "/lego/set/123-1/")

    @tag("login")
    def test_login_redirects_to_index_if_referer_is_missing(self):
        # go directly to login page
        self.driver.get(f"{self.live_server_url}/lego/login/")

        # log in
        self.driver.find_element(By.ID, "id_username").send_keys("test-user")
        input_field = self.driver.find_element(By.ID, "id_password")
        input_field.send_keys("test-password")
        input_field.submit()

        # redirected to index page
        self.wait.until(EC.title_contains("Home"))
        self.assertEndsWith(self.driver.current_url, "/lego/")
