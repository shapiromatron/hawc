import re

import pytest
from rest_framework.serializers import ValidationError

from hawc.apps.animal import models
from hawc.apps.assessment.models import Assessment


@pytest.mark.django_db
class TestEndpointManager:
    def test_bad_update_terms(self):
        assessment = Assessment.objects.get(pk=3)
        bad_endpoint_id = 1
        valid_endpoint_id = 2
        # empty data
        data = []
        expected_error = "List of endpoints must be > 1"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # missing id
        data = [{"system_term_id": 1}]
        expected_error = "Each endpoint must have an 'id'"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # non-unique ids
        data = [
            {"id": valid_endpoint_id, "system_term_id": 1},
            {"id": valid_endpoint_id, "system_term_id": 2},
        ]
        expected_error = "Endpoint ids must be unique'"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # bad id
        data = [{"id": -1, "system_term_id": 1}]
        expected_error = "Invalid id(s) -1"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # ids from different assessments
        data = [
            {"id": valid_endpoint_id, "system_term_id": 1},
            {"id": bad_endpoint_id, "system_term_id": 1},
        ]
        expected_error = "Endpoints must be from the same assessment"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # no terms
        data = [{"id": valid_endpoint_id}]
        expected_error = f"No term fields given for endpoint {valid_endpoint_id}"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # fields other than terms
        data = [{"id": valid_endpoint_id, "system_term_id": 1, "assessment": 1}]
        expected_error = "Invalid field name(s) 'assessment'"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # mismatched term types
        data = [{"id": valid_endpoint_id, "system_term_id": 2}]
        expected_error = "Term 2 is not the right type for 'system_term_id'"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)

    def test_valid_update_terms(self):
        assessment = Assessment.objects.get(pk=3)
        # one endpoint
        endpoint_1 = models.Endpoint.objects.get(pk=2)
        data = [{"id": endpoint_1.id, "system_term_id": 1}]
        assert endpoint_1.system_term_id is None
        updated_endpoints = models.Endpoint.objects.update_terms(data, assessment)
        assert len(updated_endpoints) == 1
        endpoint_1.refresh_from_db()
        assert endpoint_1.system_term_id == 1 and endpoint_1.system == "Cardiovascular"
        # multiple endpoints
        endpoint_2 = models.Endpoint.objects.get(pk=7)
        data = [
            {"id": endpoint_1.pk, "organ_term_id": 2},
            {"id": endpoint_2.pk, "system_term_id": 1},
        ]
        assert endpoint_1.organ_term_id is None
        assert endpoint_2.system_term_id is None
        updated_endpoints = models.Endpoint.objects.update_terms(data, assessment)
        assert len(updated_endpoints) == 2
        endpoint_1.refresh_from_db()
        endpoint_2.refresh_from_db()
        assert endpoint_1.organ_term_id == 2 and endpoint_1.organ == "Serum"
        assert endpoint_2.system_term_id == 1 and endpoint_2.system == "Cardiovascular"
        # multiple terms
        data = [{"id": endpoint_1.pk, "effect_term_id": 3, "effect_subtype_term_id": 4}]
        assert endpoint_1.effect_term_id is None and endpoint_1.effect_subtype_term_id is None
        updated_endpoints = models.Endpoint.objects.update_terms(data, assessment)
        assert len(updated_endpoints) == 1
        endpoint_1.refresh_from_db()
        assert endpoint_1.effect_term_id == 3 and endpoint_1.effect == "Fatty Acids"
        assert (
            endpoint_1.effect_subtype_term_id == 4
            and endpoint_1.effect_subtype == "Clinical Chemistry"
        )
