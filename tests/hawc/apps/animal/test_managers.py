import re

import pytest
from rest_framework.serializers import ValidationError

from hawc.apps.animal import models
from hawc.apps.assessment.models import Assessment


@pytest.mark.django_db
class TestEndpointManager:
    def test_bad_update_terms(self):
        assessment = Assessment.objects.get(pk=1)
        bad_endpoint_id = 3
        valid_endpoint_id = 1
        # empty data
        data = []
        expected_error = "List of endpoints must be > 1"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # missing id
        data = [{"name_term_id": 5}]
        expected_error = "Expected endpoint keys are id and name_term_id"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # non-unique ids
        data = [
            {"id": valid_endpoint_id, "name_term_id": 5},
            {"id": valid_endpoint_id, "name_term_id": 5},
        ]
        expected_error = "Endpoint ids must be unique"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # bad id
        data = [{"id": -1, "name_term_id": 5}]
        expected_error = "Invalid endpoint id(s) -1"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # ids from different assessments
        data = [
            {"id": valid_endpoint_id, "name_term_id": 5},
            {"id": bad_endpoint_id, "name_term_id": 5},
        ]
        expected_error = "Endpoints must be from the same assessment"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # missing name term
        data = [{"id": valid_endpoint_id}]
        expected_error = "Expected endpoint keys are id and name_term_id"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # bad term id
        data = [{"id": valid_endpoint_id, "name_term_id": -1}]
        expected_error = "Invalid term id(s) -1"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)
        # wrong term type
        data = [{"id": valid_endpoint_id, "name_term_id": 1}]
        expected_error = "Term id(s) 1 are not type endpoint_name"
        with pytest.raises(ValidationError, match=re.escape(expected_error)):
            models.Endpoint.objects.update_terms(data, assessment)

    def _test_updated_terms(self, endpoint):
        field_to_value = {
            "name_term_id": 5,
            "effect_subtype_term_id": 4,
            "effect_term_id": 3,
            "organ_term_id": 2,
            "system_term_id": 1,
            "name": "Fatty Acid Balance",
            "effect_subtype": "Clinical Chemistry",
            "effect": "Fatty Acids",
            "organ": "Serum",
            "system": "Cardiovascular",
        }
        for field in field_to_value:
            assert getattr(endpoint, field) == field_to_value[field]

    def test_valid_update_terms(self):
        assessment = Assessment.objects.get(pk=1)
        endpoint = models.Endpoint.objects.get(pk=1)
        assert endpoint.name_term_id is None
        data = [{"id": endpoint.id, "name_term_id": 5}]
        updated_endpoints = models.Endpoint.objects.update_terms(data, assessment)
        assert len(updated_endpoints) == 1
        endpoint.refresh_from_db()
        self._test_updated_terms(endpoint)
