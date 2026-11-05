import pytest
from django.urls import reverse
from model_bakery.baker import make

from hawc.apps.vocab.constants import Ontology, VocabularyNamespace, VocabularyTermType
from hawc.apps.vocab.models import Entity, EntityTermRelation, Term


def chain(namespace, prefix):
    system = make(Term, namespace=namespace, type=VocabularyTermType.system, name=f"{prefix} system")
    organ = make(Term, namespace=namespace, type=VocabularyTermType.organ, parent=system, name=f"{prefix} organ")
    effect = make(Term, namespace=namespace, type=VocabularyTermType.effect, parent=organ, name=f"{prefix} effect")
    subtype = make(Term, namespace=namespace, type=VocabularyTermType.effect_subtype, parent=effect, name=f"{prefix} subtype")
    endpoint = make(Term, namespace=namespace, type=VocabularyTermType.endpoint_name, parent=subtype, name=f"{prefix} endpoint")
    return system, organ, effect, subtype, endpoint


@pytest.mark.django_db
class TestTerm:
    def test_attributes_and_deprecated(self):
        term = make(Term, namespace=VocabularyNamespace.EHV, type=VocabularyTermType.system, name="System", uid=8100)
        assert str(term) == "EHV::system::System"
        assert term.deprecated is False
        assert term.get_admin_edit_url() == reverse("admin:vocab_term_change", args=(term.id,))
        term.deprecated_on = term.created_on
        term.save()
        assert term.deprecated is True

    def test_inheritance_ehv(self):
        system, organ, effect, subtype, endpoint = chain(VocabularyNamespace.EHV, "ehv")
        result = endpoint.inheritance()
        assert result["system"] == system.name
        assert result["organ"] == organ.name
        assert result["effect_term_id"] == effect.id
        assert result["name_term_id"] == endpoint.id

    def test_inheritance_toxrefdb(self):
        system, effect, subtype, endpoint = None, None, None, None
        system = make(Term, namespace=VocabularyNamespace.ToxRefDB, type=1, name="tox system", uid=8200)
        effect = make(Term, namespace=VocabularyNamespace.ToxRefDB, type=3, parent=system, name="tox effect")
        subtype = make(Term, namespace=VocabularyNamespace.ToxRefDB, type=4, parent=effect, name="tox subtype")
        endpoint = make(Term, namespace=VocabularyNamespace.ToxRefDB, type=5, parent=subtype, name="tox endpoint")
        result = endpoint.inheritance()
        assert result["system"] == system.name
        assert result["organ"] is None
        assert result["name"] == endpoint.name

    def test_dataframes(self):
        chain(VocabularyNamespace.EHV, "df ehv")
        make(Term, namespace=VocabularyNamespace.ToxRefDB, type=1, name="df tox", uid=8300)
        assert not Term.ehv_dataframe().empty
        assert not Term.toxrefdb_dataframe().empty
        assert not Term.vocab_dataframe(VocabularyNamespace.EHV).empty


@pytest.mark.django_db
class TestEntity:
    def test_external_url_and_relation(self):
        entity = make(Entity, ontology=Ontology.umls, uid="C999999")
        term = make(Term, uid=8400)
        relation = make(EntityTermRelation, entity=entity, term=term)
        assert str(entity) == "C999999"
        assert "C999999" in entity.get_external_url()
        assert str(relation) == f"{term} -> {entity}"

@pytest.mark.django_db
def test_invalid_namespace_and_unknown_ontology_raise():
    term = make(Term, namespace=99, type=1, name="invalid", uid=8900)
    with pytest.raises(ValueError):
        term.inheritance()
    entity = make(Entity, ontology=99, uid="bad-ontology")
    with pytest.raises(ValueError):
        entity.get_external_url()

@pytest.mark.django_db
def test_namespace_properties():
    assert VocabularyNamespace.display_choices()
    assert VocabularyNamespace.EHV.display_name.startswith("EPA")
    assert VocabularyNamespace.ToxRefDB.display_name.startswith("EPA")
    assert VocabularyNamespace.EHV.display_url == reverse("vocab:ehv-browse")
    assert VocabularyNamespace.ToxRefDB.display_url == reverse("vocab:toxrefdb-browse")

@pytest.mark.django_db
def test_constants_mappings_and_admin_queryset():
    from django.contrib import admin
    from django.test import RequestFactory
    from hawc.apps.vocab.admin import TermAdmin
    assert VocabularyTermType.value_to_text_field()[5] == "name"
    assert VocabularyTermType.value_to_term_field()[5] == "name_term_id"
    admin_obj = TermAdmin(Term, admin.site)
    request = RequestFactory().get("/admin/vocab/term/")
    assert admin_obj.get_queryset(request).count() >= 1
    assert admin_obj.has_delete_permission(request) is False
