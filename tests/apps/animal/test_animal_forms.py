import pytest

from hawc.apps.study.models import Study
from hawc.apps.animal.forms import ExperimentForm


def assert_field_has_error(form, field, msg):
    form.full_clean()
    assert msg in form.errors[field]


@pytest.mark.django_db
def test_experiment_form(db_keys):
    study = Study.objects.get(id=db_keys.study_working)
    inputs = {
        "name": "Example",
        "type": "Ac",
        "purity_available": False,
        "purity_qualifier": "",
        "purity": None,
    }
    form = ExperimentForm(inputs, parent=study)
    assert form.is_valid()

    inputs2 = inputs.copy()
    inputs2.update(purity_available=True, purity=None, purity_qualifier="")
    form = ExperimentForm(inputs2, parent=study)
    assert form.is_valid() is False
    assert_field_has_error(form, "purity", ExperimentForm.PURITY_REQ)
    assert_field_has_error(form, "purity_qualifier", ExperimentForm.PURITY_QUALIFIER_REQ)

    inputs3 = inputs.copy()
    inputs3.update(purity_available=True, purity=None, purity_qualifier="")
    inputs3.update(purity_available=False, purity=95, purity_qualifier=">")
    form = ExperimentForm(inputs3, parent=study)
    assert form.is_valid() is False
    assert_field_has_error(form, "purity", ExperimentForm.PURITY_NOT_REQ)
    assert_field_has_error(form, "purity_qualifier", ExperimentForm.PURITY_QUALIFIER_NOT_REQ)
