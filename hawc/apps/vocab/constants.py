from typing import Dict, List

from django.utils.functional import classproperty

from ..common.constants import IntChoiceEnum


class VocabularyNamespace(IntChoiceEnum):
    """
    A namespace for a vocabulary. HAWC will not enforce a single vocabulary, this can be controlled
    at the assessment level.
    """

    EHV = 1  # environmental health vocabulary

    @classproperty
    def display_dict(cls) -> Dict:
        return {1: "EPA Environmental health vocabulary"}

    @classmethod
    def display_choices(cls) -> List:
        return [(key, value) for key, value in cls.display_dict.items()]

    @property
    def display_name(self) -> str:
        return self.display_dict[self.value]


class VocabularyTermType(IntChoiceEnum):
    """
    Vocabulary will be associated with certain fields in HAWC. This enum allows us to map the vocab.
    """

    system = 1
    organ = 2
    effect = 3
    effect_subtype = 4
    endpoint_name = 5

    @classmethod
    def value_to_text_field(cls) -> Dict:
        return {
            cls.system.value: "system",
            cls.organ.value: "organ",
            cls.effect.value: "effect",
            cls.effect_subtype.value: "effect_subtype",
            cls.endpoint_name.value: "name",
        }

    @classmethod
    def value_to_term_field(cls) -> Dict:
        return {
            cls.system.value: "system_term_id",
            cls.organ.value: "organ_term_id",
            cls.effect.value: "effect_term_id",
            cls.effect_subtype.value: "effect_subtype_term_id",
            cls.endpoint_name.value: "name_term_id",
        }


class Ontology(IntChoiceEnum):
    """
    Ontology for for UID
    """

    umls = 1
