from django.conf import settings
from selectable.forms import *  # noqa
from selectable.forms.widgets import SelectableMediaMixin

SelectableMediaMixin.Media.js = (
    *SelectableMediaMixin.Media.js,
    str(settings.PROJECT_PATH / "static/js/selectable_bootstrap.js"),
)

