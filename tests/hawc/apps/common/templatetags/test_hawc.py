import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.common.templatetags.hawc import admin_url, e_notation, hastext


@pytest.mark.django_db
def test_admin_url():
    assessment = Assessment.objects.get(id=1)
    url = admin_url(assessment)
    assert url == "/admin/assessment/assessment/1/change/"


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
            ("a", "a"),
            (None, "None"),
            (1.2345e-05, "1.2345e-05"),
            (1e-05, "1.00e-05"),
            (0.00012345, "0.00012345"),
            (0.0001, "0.0001"),
            (0.0015, "0.0015"),
            (0.001, "0.001"),
            (0.1, "0.1"),
            (1, "1"),
            (10, "10"),
            (99999.9, "99999.9"),
            (1000000, "1.00e+06"),
            (1234567, "1.23e+06"),
        ],
    )
    def test_e_notation(self, input, output):
        assert e_notation(input) == output
