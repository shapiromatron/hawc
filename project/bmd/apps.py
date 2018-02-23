from django.apps import AppConfig
from django.conf import settings

import os


class BMDConfig(AppConfig):
    name = 'bmd'
    verbose_name = 'Benchmark dose modeling'

    def ready(self):
        # load signals
        from . import bmds_monkeypatch, models, signals  # noqa

        # ensure media upload path exists
        path = os.path.abspath(
            os.path.join(
                settings.MEDIA_ROOT,
                models.Model.IMAGE_UPLOAD_TO,
            )
        )

        if not os.path.exists(path):
            os.makedirs(path)
