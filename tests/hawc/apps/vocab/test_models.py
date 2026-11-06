import pytest
from django.urls import reverse
from model_bakery.baker import make

from hawc.apps.vocab.constants import Ontology, VocabularyNamespace, VocabularyTermType
from hawc.apps.vocab.models import Entity, EntityTermRelation, Term


def chain(namespace, prefix):
    system = make(
        Term, namespace=namespace, type=VocabularyTermType.system, name=f"{prefix} system"
    )
    organ = make(
        Term,
        namespace=namespace,
        type=VocabularyTermType.organ,
        parent=system,
        name=f"{prefix} organ",
    )
    effect = make(
        Term,
        namespace=namespace,
        type=VocabularyTermType.effect,
        parent=organ,
        name=f"{prefix} effect",
    )
    subtype = make(
        Term,
        namespace=namespace,
        type=VocabularyTermType.effect_subtype,
        parent=effect,
        name=f"{prefix} subtype",
    )
    endpoint = make(
        Term,
        namespace=namespace,
        type=VocabularyTermType.endpoint_name,
        parent=subtype,
        name=f"{prefix} endpoint",
    )
    return system, organ, effect, subtype, endpoint


def tox_chain(prefix):
    system = make(
        Term,
        namespace=VocabularyNamespace.ToxRefDB,
        type=VocabularyTermType.system,
        name=f"{prefix} system",
    )
    effect = make(
        Term,
        namespace=VocabularyNamespace.ToxRefDB,
        type=VocabularyTermType.effect,
        parent=system,
        name=f"{prefix} effect",
    )
    subtype = make(
        Term,
        namespace=VocabularyNamespace.ToxRefDB,
        type=VocabularyTermType.effect_subtype,
        parent=effect,
        name=f"{prefix} subtype",
    )
    endpoint = make(
        Term,
        namespace=VocabularyNamespace.ToxRefDB,
        type=VocabularyTermType.endpoint_name,
        parent=subtype,
        name=f"{prefix} endpoint",
    )
    return system, effect, subtype, endpoint


@pytest.mark.django_db
class TestTerm:
    def test_attributes_and_deprecated(self):
        term = make(
            Term,
            namespace=VocabularyNamespace.EHV,
            type=VocabularyTermType.system,
            name="System",
            uid=8100,
        )
        assert str(term) == "EHV::system::System"
        assert term.deprecated is False
        assert term.get_admin_edit_url() == reverse("admin:vocab_term_change", args=(term.id,))
        term.deprecated_on = term.created_on
        term.save()
        assert term.deprecated is True

    def test_inheritance_ehv(self):
        system, organ, effect, _subtype, endpoint = chain(VocabularyNamespace.EHV, "ehv")
        result = endpoint.inheritance()
        assert result["system"] == system.name
        assert result["organ"] == organ.name
        assert result["effect_term_id"] == effect.id
        assert result["name_term_id"] == endpoint.id

    def test_inheritance_toxrefdb(self):
        system, effect, _subtype, endpoint = tox_chain("tox")
        result = endpoint.inheritance()
        assert result["system"] == system.name
        assert result["organ"] is None
        assert result["effect_term_id"] == effect.id
        assert result["name"] == endpoint.name

    def test_dataframes(self):
        chain(VocabularyNamespace.EHV, "df ehv")
        _system, _effect, _subtype, endpoint = tox_chain("df tox")
        assert not Term.ehv_dataframe().empty
        toxrefdb = Term.toxrefdb_dataframe()
        assert endpoint.name in toxrefdb["name"].values
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
