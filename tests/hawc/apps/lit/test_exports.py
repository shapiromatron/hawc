import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit import exports, models


@pytest.mark.django_db
class TestReferenceTagLongExport:
    def test_success(self):
        exporter = exports.ReferenceTagLongExport(
            queryset=models.Reference.objects.filter(assessment_id=2),
            assessment=Assessment.objects.get(id=2),
        )
        assert exporter.build_df().shape == (5, 10)

    def test_no_data(self):
        exporter = exports.ReferenceTagLongExport(
            queryset=models.Reference.objects.filter(assessment_id=5),
            assessment=Assessment.objects.get(id=5),
        )
        df = exporter.build_df()
        assert df.shape == (1, 1)
        assert df.Result[0] == "No data available."


@pytest.mark.django_db
class TestReferenceFlatComplete:
    def test_get_identifiers_df(self):
        qs = models.Reference.objects.filter(assessment_id=2).order_by("id")
        exporter = exports.ReferenceFlatComplete(queryset=qs)
        df = exporter._get_identifiers_df()
        assert df.fillna("").to_dict(orient="list") == {
            "HAWC ID": [5, 6, 7, 8, 12],
            "DOI": ["10.1093/milmed/166.suppl_2.23", "", "", "", ""],
            "PubMed ID": [11778423, 15907334, 21284075, 24004895, 28572920],
        }
