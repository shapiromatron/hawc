import pytest

from hawc.apps.animal import forms, models
from hawc.apps.study.models import Study


def assert_field_has_error(form, field, msg):
    form.full_clean()
    assert msg in form.errors[field]


@pytest.mark.django_db
class TestExperimentForm:
    def test_form(self, db_keys):
        study = Study.objects.get(id=db_keys.study_working)
        inputs = {
            "name": "Example",
            "type": "Ac",
            "purity_available": False,
            "purity_qualifier": "",
            "purity": None,
        }
        form = forms.ExperimentForm(inputs, parent=study)
        assert form.is_valid()

        inputs2 = inputs.copy()
        inputs2.update(purity_available=True, purity=None, purity_qualifier="")
        form = forms.ExperimentForm(inputs2, parent=study)
        assert form.is_valid() is False
        assert_field_has_error(form, "purity", forms.ExperimentForm.PURITY_REQ)
        assert_field_has_error(form, "purity_qualifier", forms.ExperimentForm.PURITY_QUALIFIER_REQ)

        inputs3 = inputs.copy()
        inputs3.update(purity_available=True, purity=None, purity_qualifier="")
        inputs3.update(purity_available=False, purity=95, purity_qualifier=">")
        form = forms.ExperimentForm(inputs3, parent=study)
        assert form.is_valid() is False
        assert_field_has_error(form, "purity", forms.ExperimentForm.PURITY_NOT_REQ)
        assert_field_has_error(
            form, "purity_qualifier", forms.ExperimentForm.PURITY_QUALIFIER_NOT_REQ
        )


@pytest.mark.django_db
class TestEndpointForm:
    def test_clean_endpoint(self, db_keys):
        # set a valid instance initially
        animal_group = models.AnimalGroup.objects.get(id=db_keys.animal_group_working)
        baseline_data = {
            "name": "foo",
            "NOEL": -999,
            "LOEL": -999,
            "FEL": -999,
            "data_type": "C",
            "variance_type": 1,
            "observation_time_units": 0,
            "expected_adversity_direction": 4,
            "monotonicity": 8,
            "trend_result": 3,
            "litter_effects": "NA",
            "data_extracted": True,
            "response_units": "μg/dL",
        }
        form = forms.EndpointForm(
            baseline_data, parent=animal_group, assessment=animal_group.get_assessment()
        )
        assert form.is_valid() is True

        # observation time units
        data = baseline_data.copy()
        data.update(observation_time=123)
        form = forms.EndpointForm(
            data, parent=animal_group, assessment=animal_group.get_assessment()
        )
        assert form.is_valid() is False
        assert form.errors == {"observation_time_units": [forms.EndpointForm.OBS_TIME_UNITS_REQ]}

        # observation time
        data = baseline_data.copy()
        data.update(observation_time_units=1)
        form = forms.EndpointForm(
            data, parent=animal_group, assessment=animal_group.get_assessment()
        )
        assert form.is_valid() is False
        assert form.errors == {"observation_time": [forms.EndpointForm.OBS_TIME_VALUE_REQ]}

        # percent different range
        data = baseline_data.copy()
        data.update(data_type="P")
        form = forms.EndpointForm(
            data, parent=animal_group, assessment=animal_group.get_assessment()
        )
        assert form.is_valid() is False
        assert form.errors == {"confidence_interval": [forms.EndpointForm.CONF_INT_REQ]}

        # variance_type
        data = baseline_data.copy()
        data.update(variance_type=0)
        form = forms.EndpointForm(
            data, parent=animal_group, assessment=animal_group.get_assessment()
        )
        assert form.is_valid() is False
        assert form.errors == {"variance_type": [forms.EndpointForm.VAR_TYPE_REQ]}

        # response_units
        data = baseline_data.copy()
        data.pop("response_units")
        form = forms.EndpointForm(
            data, parent=animal_group, assessment=animal_group.get_assessment()
        )
        assert form.is_valid() is False
        assert form.errors == {"response_units": [forms.EndpointForm.RESP_UNITS_REQ]}

        # litter_effect_notes
        data = baseline_data.copy()
        data.update(
            litter_effects="O",
            litter_effect_notes="",
        )
        form = forms.EndpointForm(
            data, parent=animal_group, assessment=animal_group.get_assessment()
        )
        assert form.is_valid() is False
        assert form.errors == {
            "litter_effects": [forms.EndpointForm.LIT_EFF_NOT_REQ],  # based on experimental design
            "litter_effect_notes": [forms.EndpointForm.LIT_EFF_NOTES_REQ],
        }

        # TODO - not all `litter_effect` cases are tested; some depend on experimental design


@pytest.mark.django_db
class TestEndpointGroupForm:
    def test_clean_endpoint_group(self, db_keys):
        # continuous
        resp = forms.EndpointGroupForm.clean_endpoint_group(
            "C", 1, {"n": 1, "response": 1, "variance": 1}
        )
        assert len(resp) == 0
        resp = forms.EndpointGroupForm.clean_endpoint_group("C", 0, {"variance": 1})
        assert resp == {"variance": forms.EndpointGroupForm.VARIANCE_REQ}

        # percent difference
        resp = forms.EndpointGroupForm.clean_endpoint_group(
            "P", 0, {"n": 1, "lower_ci": 1, "upper_ci": 1}
        )
        assert len(resp) == 0
        resp = forms.EndpointGroupForm.clean_endpoint_group("P", 0, {"lower_ci": 1})
        assert resp == {"upper_ci": forms.EndpointGroupForm.UPPER_CI_REQ}
        resp = forms.EndpointGroupForm.clean_endpoint_group("P", 0, {"upper_ci": 1})
        assert resp == {"lower_ci": forms.EndpointGroupForm.LOWER_CI_REQ}
        resp = forms.EndpointGroupForm.clean_endpoint_group("P", 0, {"lower_ci": 1, "upper_ci": 0})
        assert resp == {"lower_ci": forms.EndpointGroupForm.LOWER_CI_GT_UPPER}

        # dichotomous
        resp = forms.EndpointGroupForm.clean_endpoint_group("D", 0, {"n": 1, "incidence": 0})
        assert len(resp) == 0
        resp = forms.EndpointGroupForm.clean_endpoint_group("D", 0, {"incidence": 1})
        assert resp == {"n": forms.EndpointGroupForm.N_REQ}
        resp = forms.EndpointGroupForm.clean_endpoint_group("D", 0, {"n": 1})
        assert resp == {"incidence": forms.EndpointGroupForm.INC_REQ}
        resp = forms.EndpointGroupForm.clean_endpoint_group("D", 0, {"n": 1, "incidence": 2})
        assert resp == {"incidence": forms.EndpointGroupForm.POS_N_REQ}


@pytest.mark.django_db
class TestMultipleEndpointChoiceField:
    def test_success(self, db_keys, django_assert_max_num_queries):
        # check widget returns and uses our efficient queryset
        qs = models.Endpoint.objects.assessment_qs(db_keys.assessment_final).selector()
        field = forms.MultipleEndpointChoiceField(queryset=qs)

        with django_assert_max_num_queries(1):
            options = list(field.widget.options("test", []))

        # check label looks correct
        assert len(options) >= 5
        labels = {option["label"] for option in options}
        assert "Biesemeier JA et al. 2011 | developmental | sd rats | bmd3 - continuous" in labels
