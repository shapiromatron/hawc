import pytest

from hawc.apps.vocab.constants import VocabularyNamespace
from hawc.apps.vocab.models import Entity, Term


@pytest.mark.django_db
class TestTerm:
    def test_inheritance(self):
        # ehv
        term = Term.objects.get(id=5)
        endpoint = term.inheritance()
        assert term.namespace == VocabularyNamespace.EHV
        assert endpoint["name"] == "Fatty Acid Balance"
        assert endpoint["system"] == "Cardiovascular"
        # toxrefdb
        term = Term.objects.get(id=7003)
        endpoint = term.inheritance()
        assert term.namespace == VocabularyNamespace.ToxRefDB
        assert endpoint["name"] == "dysplasia"
        assert endpoint["system"] == "systemic"


@pytest.mark.django_db
class TestEntity:
    def test_attributes(self):
        entity = Entity.objects.get(id=1)
        assert str(entity) == "C0015684"
        assert (
            entity.get_external_url()
            == "https://ncim.nci.nih.gov/ncimbrowser/pages/concept_details.jsf?dictionary=NCI%20Metathesaurus&code=C0015684"
        )
