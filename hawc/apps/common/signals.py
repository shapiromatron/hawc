from contextlib import contextmanager
from itertools import chain

from django.db.models import signals as dsignals
from django.dispatch import Signal


@contextmanager
def ignore_signals():
    """
    Temporarily ignore django model signals for all models.

    Originally taken from: https://www.cameronmaske.com/muting-django-signals-with-a-pytest-fixture/
    """
    signals = [
        signal
        for signal in chain(
            dsignals.__dict__.values(),
        )
        if isinstance(signal, Signal)
    ]
    restore = {}
    for signal in signals:
        restore[signal] = signal.receivers
        signal.receivers = []

    try:
        yield

    finally:
        for signal, receivers in restore.items():
            signal.receivers = receivers
