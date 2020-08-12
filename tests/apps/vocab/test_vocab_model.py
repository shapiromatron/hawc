import pytest
from hawc.apps.vocab.models import Term, Entity


@pytest.mark.django_db
class TestTerm:
    def test_attributes(self):
        term = Term.objects.get(id=1)
        assert str(term) == "EHV::system::Cardiovascular"
        assert (
            term.get_admin_edit_url()
            == "/admin/f09ea0b8-c3d5-4ff9-86c4-27f00e8f643d/vocab/term/1/change/"
        )


@pytest.mark.django_db
class TestEntity:
    def test_attributes(self):
        entity = Entity.objects.get(id=1)
        assert str(entity) == "C0015684"
        assert (
            entity.get_external_url()
            == "https://ncim.nci.nih.gov/ncimbrowser/pages/concept_details.jsf?dictionary=NCI%20Metathesaurus&code=C0015684"
        )
