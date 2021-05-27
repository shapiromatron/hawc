from textwrap import dedent

import pytest
from django.urls import reverse

from hawc.apps.riskofbias.models import RiskOfBiasScoreOverrideObject


@pytest.mark.django_db
class TestRiskOfBiasScoreOverrideObject:
    def test_get_object_url(self):
        valid = RiskOfBiasScoreOverrideObject.objects.get(id=2)
        assert valid.get_object_url() == valid.content_object.get_absolute_url()

        invalid = RiskOfBiasScoreOverrideObject.objects.get(id=3)
        assert invalid.get_object_url() == reverse("404")

    def test_get_object_name(self):
        valid = RiskOfBiasScoreOverrideObject.objects.get(id=2)
        assert valid.get_object_name() == "sd rats"

        invalid = RiskOfBiasScoreOverrideObject.objects.get(id=3)
        assert "deleted" in invalid.get_object_name()

    def test_get_orphan_relations(self):
        actual = RiskOfBiasScoreOverrideObject.get_orphan_relations()
        expected = dedent(
            """
            Found orphaned RiskOfBiasScoreOverrideObjects:
            id=3;score=16;obj_ct=49;obj_id=99999
            """
        ).strip()
        assert actual == expected
