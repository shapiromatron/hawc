import datetime
from unittest.mock import patch

import pytest

from hawc.apps.assessment.widgets import DateCheckboxInput

# mock timezone.now() for consistent testing
NOW_FOR_TESTING = datetime.datetime(2021, 10, 10, 10, 10, 10)


def mock_now():
    return NOW_FOR_TESTING


@pytest.mark.django_db
@patch("django.utils.timezone.now", side_effect=mock_now)
class TestDateCheckboxInput:

    widget = DateCheckboxInput()

    def test_value_from_datadict(self, *args):
        """
        The DateCheckboxInput widget will return None if the data is empty or 'false', returns timezone.now() if it is 'true'
        """

        assert self.widget.value_from_datadict({}, {}, "testing") is None
        assert self.widget.value_from_datadict({"testing": "false"}, {}, "testing") is None
        assert (
            self.widget.value_from_datadict({"testing": "true"}, {}, "testing") == NOW_FOR_TESTING
        )
