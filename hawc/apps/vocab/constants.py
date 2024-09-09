from django.db.models import IntegerChoices
from django.utils.functional import classproperty


class VocabularyNamespace(IntegerChoices):
    """
    A namespace for a vocabulary. HAWC will not enforce a single vocabulary, this can be controlled
    at the assessment level.
    """

    EHV = 1, "EHV"
    ToxRefDB = 2, "ToxRefDB"

    @classproperty
    def display_dict(cls) -> dict:
        return {1: "EPA Environmental health vocabulary", 2: "EPA ToxRefDB vocabulary"}

    @classmethod
    def display_choices(cls) -> list:
        return [(key, value) for key, value in cls.display_dict.items()]

    @property
    def display_name(self) -> str:
        return self.display_dict[self.value]


class VocabularyTermType(IntegerChoices):
    """
    Vocabulary will be associated with certain fields in HAWC. This enum allows us to map the vocab.
    """

    system = 1, "system"
    organ = 2, "organ"
    effect = 3, "effect"
    effect_subtype = 4, "effect_subtype"
    endpoint_name = 5, "endpoint_name"

    @classmethod
    def value_to_text_field(cls) -> dict:
        return {
            cls.system.value: "system",
            cls.organ.value: "organ",
            cls.effect.value: "effect",
            cls.effect_subtype.value: "effect_subtype",
            cls.endpoint_name.value: "name",
        }

    @classmethod
    def value_to_term_field(cls) -> dict:
        return {
            cls.system.value: "system_term_id",
            cls.organ.value: "organ_term_id",
            cls.effect.value: "effect_term_id",
            cls.effect_subtype.value: "effect_subtype_term_id",
            cls.endpoint_name.value: "name_term_id",
        }


class Ontology(IntegerChoices):
    """
    Ontology for for UID
    """

    umls = 1, "UMLS"
