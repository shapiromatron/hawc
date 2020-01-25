from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, m2m_changed
import logging
import pytest

from django.core.management import call_command

from fixtures import *  # noqa: F401, F403


@pytest.fixture(scope="session", autouse=True)
def test_db(django_db_setup, django_db_blocker):
    logging.info("Loading db fixture...")

    # ignore signals
    # see https://www.cameronmaske.com/muting-django-signals-with-a-pytest-fixture/
    signals = [pre_save, post_save, pre_delete, post_delete, m2m_changed]
    restore = {}
    for signal in signals:
        # Temporally remove the signal's receivers (a.k.a attached functions)
        restore[signal] = signal.receivers
        signal.receivers = []

    with django_db_blocker.unblock():
        call_command("flush", verbosity=0, interactive=False)
        call_command("loaddata", "tests/data/fixtures/db.yaml", verbosity=0)

    # restore signals.
    for signal, receivers in restore.items():
        signal.receivers = receivers
