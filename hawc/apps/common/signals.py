from contextlib import contextmanager

from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save


@contextmanager
def ignore_signals():
    """
    Temporarily ignore django model signals for all models.

    Originally taken from: https://www.cameronmaske.com/muting-django-signals-with-a-pytest-fixture/
    """
    signals = [pre_save, post_save, pre_delete, post_delete, m2m_changed]
    restore = {}
    for signal in signals:
        restore[signal] = signal.receivers
        signal.receivers = []

    try:
        yield

    finally:
        for signal, receivers in restore.items():
            signal.receivers = receivers
