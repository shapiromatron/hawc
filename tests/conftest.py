import json
import logging
import os
import time
from pathlib import Path
from typing import NamedTuple

import helium
import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import connections
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

CI = os.environ.get("CI") == "true"
SHOW_BROWSER = bool(os.environ.get("SHOW_BROWSER", None))


class UserCredential(NamedTuple):
    email: str
    password: str


class Keys:
    """
    Lookup to test specific objects in the text-fixture.
    """

    def __init__(self):
        self.assessment_working = 1
        self.assessment_final = 2
        self.assessment_client = 3
        self.assessment_keys = [1, 2]

        self.dataset_final = 2
        self.dataset_working = 1
        self.dataset_unpublished = 3

        self.study_working = 1
        self.study_final_bioassay = 7

        self.reference_linked = 1
        self.reference_unlinked = 3

        self.animal_group_working = 1
        self.endpoint_working = 1

        self.riskofbias_assessment_working_metric_ids = [1, 2]

        self.visual_heatmap = 1
        self.visual_barchart = 2

        self.pm_user = UserCredential("pm@hawcproject.org", "pw")
        self.pm_user_id = 2

        self.job_assessment = "204faaa7-fdfa-4426-a09f-f0d1af9db33d"
        self.job_global = "08ca9f23-5368-4ed6-9b18-29625add9aa8"

        self.log_assessment = 1
        self.log_global = 2

        self.blog_published = 2
        self.blog_unpublished = 1


_keys = Keys()


@pytest.fixture(scope="session", autouse=True)
def test_db(django_db_setup, django_db_blocker):
    logging.info("Loading db fixture...")
    with django_db_blocker.unblock():
        call_command("load_test_db")
        call_command("create_materialized_views")

        with connections["default"].cursor() as cursor:
            # since we skip migrations, apply lit.0015_unaccent manually
            cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


@pytest.fixture
def db_keys():
    return _keys


@pytest.fixture
def set_db_keys(request):
    request.cls.db_keys = _keys


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": [("authorization", "<omitted>")],
        "filter_post_data_parameters": [("api_key", "<omitted>")],
        "ignore_localhost": True,
    }


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    cassette_dir = Path(__file__).parent.absolute() / "data/cassettes" / request.module.__name__
    return str(cassette_dir)


@pytest.fixture(scope="session")
def rewrite_data_files():
    """
    If you're making changes to datasets and it's expected that previously saved data will need to
    be written, then you can set this flag to True and then all saved data will be rewritten.

    Please review changes to ensure they're expected after modifying this flag.

    A test exists in CI to ensure that this flag is set to False on commit.
    """
    return False


def _wait_until_webpack_ready(max_wait_sec: int = 60):
    """Sleep until webpack is ready...

    Raises:
        EnvironmentError: If webpack fails to complete in designated time
    """
    stats = Path(settings.WEBPACK_LOADER["DEFAULT"]["STATS_FILE"])
    waited_for = 0
    while waited_for < max_wait_sec:
        if stats.exists() and json.loads(stats.read_text()).get("status") == "done":
            return
        time.sleep(1)
        waited_for += 1
    raise EnvironmentError("Timeout; webpack dev server not ready")


def _get_driver(browser: str, CI: bool):
    """
    Returns the web-driver depending on the specified environment

    Args:
        browser (str): "firefox" or "chrome"
        CI (bool): if we're in the CI environment

    Raises:
        ValueError: if configuration is invalid
    """
    command_executor = None
    if CI:
        host = os.environ["SELENIUM_HOST"]
        port = os.environ["SELENIUM_PORT"]
        command_executor = f"http://{host}:{port}/wd/hub"

    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        if CI:
            options.headless = True
            driver = webdriver.Remote(
                command_executor=command_executor,
                desired_capabilities=DesiredCapabilities.FIREFOX,
                options=options,
            )
            helium.set_driver(driver)
            return driver
        else:
            return helium.start_firefox(options=options, headless=not SHOW_BROWSER)
    elif browser == "chrome":
        options = webdriver.ChromeOptions()
        # prevent navbar from collapsing
        options.add_argument("--window-size=1920,1080")
        if CI:
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_argument("--headless")
            driver = webdriver.Remote(
                command_executor=command_executor,
                desired_capabilities=DesiredCapabilities.CHROME,
                options=options,
            )
            helium.set_driver(driver)
            return driver
        else:
            return helium.start_chrome(options=options, headless=not SHOW_BROWSER)
    else:
        raise ValueError(f"Unknown config: {browser} / {CI}")


@pytest.fixture(scope="session")
def chrome_driver():
    driver = _get_driver("chrome", CI)
    _wait_until_webpack_ready()
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture(scope="session")
def firefox_driver():
    driver = _get_driver("firefox", CI)
    # prevent navbar from collapsing
    driver.set_window_size(1920, 1080)
    _wait_until_webpack_ready()
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def set_chrome_driver(request, chrome_driver):
    request.cls.driver = chrome_driver


@pytest.fixture
def set_firefox_driver(request, firefox_driver):
    request.cls.driver = firefox_driver
