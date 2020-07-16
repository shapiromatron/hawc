import logging
from pathlib import Path
from typing import NamedTuple

import pytest
from django.core.management import call_command


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

        self.study_working = 1
        self.study_final_bioassay = 7

        self.reference_linked = 1
        self.reference_unlinked = 3

        self.animal_group_working = 1
        self.endpoint_working = 1

        self.visual_heatmap = 1
        self.visual_barchart = 2

        self.pm_user = UserCredential("pm@pm.com", "pw")


_keys = Keys()


@pytest.fixture(scope="session", autouse=True)
def test_db(django_db_setup, django_db_blocker):
    logging.info("Loading db fixture...")
    with django_db_blocker.unblock():
        call_command("load_test_db")


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
