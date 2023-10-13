import datetime
from unittest.mock import patch

from django.db import models

from hawc.apps.common.widgets import DateCheckboxInput, SelectMultipleOtherWidget, SelectOtherWidget

# mock timezone.now() for consistent testing
NOW_FOR_TESTING = datetime.datetime(2021, 10, 10, 10, 10, 10)


def mock_now():
    return NOW_FOR_TESTING


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


class ThreeChoices(models.TextChoices):
    UNO = "uno"
    DOS = "dos"
    TRES = "tres"
    OTHER = "other"


class TestSelectOtherWidget:
    widget = SelectOtherWidget(choices=ThreeChoices.choices)

    def test_to_form(self):
        assert self.widget.decompress(None) == [None, ""]
        assert self.widget.decompress("") == [None, ""]
        assert self.widget.decompress("uno") == ["uno", ""]
        assert self.widget.decompress("cuatro") == ["other", "cuatro"]

    def test_from_form(self):
        from_dd = self.widget.value_from_datadict

        # standard cases
        assert from_dd({"test_0": "uno"}, {}, "test") == "uno"
        assert from_dd({"test_0": "uno", "test_1": ""}, {}, "test") == "uno"
        assert from_dd({"test_0": "other", "test_1": "cuatro"}, {}, "test") == "cuatro"

        # edge cases
        assert from_dd({"test_0": "other", "test_1": "  cuatro  "}, {}, "test") == "cuatro"
        assert from_dd({}, {}, "test") is None
        assert from_dd({"test_0": "uno", "test_1": "cuatro"}, {}, "test") == "uno"
        assert from_dd({"test_0": "other", "test_1": ""}, {}, "test") is None


class TestSelectMultipleOtherWidget:
    widget = SelectMultipleOtherWidget(choices=ThreeChoices.choices)

    def test_to_form(self):
        assert self.widget.decompress(None) == [[], ""]
        assert self.widget.decompress("") == [[], ""]
        assert self.widget.decompress("uno") == [["uno"], ""]
        assert self.widget.decompress("cuatro") == [["other"], "cuatro"]
        assert self.widget.decompress("dos,cuatro,cinco") == [["dos", "other"], "cuatro, cinco"]
        assert self.widget.decompress("dos,, ,cuatro,cinco") == [["dos", "other"], "cuatro, cinco"]
        assert self.widget.decompress(["dos", "cuatro", "cinco"]) == [
            ["dos", "other"],
            "cuatro, cinco",
        ]

    def test_from_form(self):
        from_dd = self.widget.value_from_datadict
        assert from_dd({}, {}, "test") is None
        assert from_dd({"test_0": ["uno", "dos"]}, {}, "test") == ["uno", "dos"]
        assert from_dd({"test_0": ["uno"], "test_1": "cuatro"}, {}, "test") == ["uno"]
        assert from_dd({"test_0": ["other"], "test_1": ""}, {}, "test") is None
        assert from_dd({"test_0": ["other"], "test_1": "cuatro"}, {}, "test") == ["cuatro"]
        assert from_dd({"test_0": ["uno", "other"], "test_1": "cuatro"}, {}, "test") == [
            "uno",
            "cuatro",
        ]

        assert from_dd({"test_0": ["other"], "test_1": ",,, , , "}, {}, "test") is None

        for naughty_other in [
            "cuatro,cinco",
            "cuatro, cinco",
            " cuatro,  cinco ",
            "cuatro,,cinco",
            "cuatro,,,,cinco,,,",
        ]:
            assert from_dd({"test_0": ["other"], "test_1": naughty_other}, {}, "test") == [
                "cuatro",
                "cinco",
            ]
