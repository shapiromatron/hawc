import pytest

from hawc.apps.vocab.models import Entity, Term


@pytest.mark.django_db
class TestTerm:
    def test_attributes(self):
        term = Term.objects.get(id=1)
        assert str(term) == "EHV::system::Cardiovascular"
        assert term.get_admin_edit_url() == "/admin/vocab/term/1/change/"

        term = Term.objects.get(id=7002)
        assert str(term) == "ToxRef::effect_subtype::eye"
        assert term.get_admin_edit_url() == "/admin/vocab/term/7002/change/"

    def test_ehv_endpoint(self):
        term = Term.objects.get(id=5)
        endpoint = term.ehv_endpoint_name()
        assert endpoint["name"] == "Fatty Acid Balance"
        assert endpoint["system"] == "Cardiovascular"

    def test_toxref_endpoint(self):
        term = Term.objects.get(id=7003)
        endpoint = term.toxref_endpoint_name()
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
