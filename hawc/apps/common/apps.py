import numpy as np
from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = "hawc.apps.common"

    def ready(self):
        from . import autocomplete

        np.set_printoptions(legacy="1.25")  # print numpy values as int/float

        autocomplete.autodiscover()
