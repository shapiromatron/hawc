from django.conf import settings
from selectable.forms import *  # noqa
from selectable.forms.widgets import SelectableMediaMixin

SelectableMediaMixin.Media.js = (
    *SelectableMediaMixin.Media.js,
    settings.STATIC_URL + "js/selectable_bootstrap.js",
)
