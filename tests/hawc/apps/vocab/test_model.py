import pytest

from hawc.apps.vocab.constants import VocabularyNamespace
from hawc.apps.vocab.models import Entity, GuidelineProfile, Term


@pytest.mark.django_db
class TestTerm:
    def test_attributes(self):
        term = Term.objects.get(id=1)
        assert str(term) == "EHV::system::Cardiovascular"
        assert term.get_admin_edit_url() == "/admin/vocab/term/1/change/"

        term = Term.objects.get(id=7002)
        assert str(term) == "ToxRefDB::effect_subtype::eye"
        assert term.get_admin_edit_url() == "/admin/vocab/term/7002/change/"

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


@pytest.mark.django_db
class TestGuidelineProfile:
    def test_attributes(self):
        profile = GuidelineProfile.objects.get(id=1)
        assert str(profile) == "90-day Oral Toxicity in Rodents:not required"
        assert profile.get_admin_edit_url() == "/admin/vocab/guidelineprofile/1/change/"
