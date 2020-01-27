import logging

import pytest
from django.core.management import call_command


class Keys:
    """
    Lookup to test specific objects in the text-fixture.
    """

    def __init__(self):
        self.assessment_working = 1
        self.assessment_final = 2
        self.assessment_keys = [1, 2]

        self.study_working = 1
        self.study_final = 2


_keys = Keys()


@pytest.fixture(scope="session", autouse=True)
def test_db(django_db_setup, django_db_blocker):
    logging.info("Loading db fixture...")
    with django_db_blocker.unblock():
        call_command("load_test_db")


@pytest.fixture
def db_keys():
    return _keys
