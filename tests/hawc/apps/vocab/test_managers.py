import pytest
from model_bakery.baker import make
from hawc.apps.animal.models import Endpoint, Study
from hawc.apps.vocab.constants import VocabularyNamespace, VocabularyTermType
from hawc.apps.vocab.models import Term


def baked_endpoint(field, uid, assessment_id=None):
    study = make(Study)
    if assessment_id is not None:
        study.assessment_id = assessment_id
        study.save(update_fields=["assessment_id"])
    term = make(Term, namespace=VocabularyNamespace.EHV, type=VocabularyTermType.system, uid=uid)
    endpoint = make(Endpoint, animal_group__experiment__study=study, **{field: term})
    return study, term, endpoint


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "field", "uid"),
    [
        ("assessment_systems", "system_term", 8500),
        ("assessment_organs", "organ_term", 8501),
        ("assessment_effects", "effect_term", 8502),
        ("assessment_effect_subtypes", "effect_subtype_term", 8503),
        ("assessment_endpoint_names", "name_term", 8504),
    ],
)
def test_assessment_manager_returns_baked_nonzero(method, field, uid):
    study, term, endpoint = baked_endpoint(field, uid)
    result = getattr(Term.objects, method)(study.assessment_id)
    assert result.filter(pk=term.pk).count() == 1
    assert result.count() > 0
