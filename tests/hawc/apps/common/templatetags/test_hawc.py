import pytest

from hawc.apps.common.templatetags.hawc import e_notation, hastext


class TestHasText:
    def test_hastext(self):
        for text in [None, "", "<p>  <br/>    \t</p>"]:
            assert hastext(text) is False
        for text in [0, False, "a", "&nbsp;", "<p>a</p>"]:
            assert hastext(text) is True


class TestENotation:
    @pytest.mark.parametrize(
        "input,output",
        [
            (1, "1"),
            (0.0009, "9.00e-04"),
            (1e-7, "1e-07"),
            (10000, "10000"),
        ],
    )
    def test_e_notation(self, input, output):
        assert e_notation(input) == output
