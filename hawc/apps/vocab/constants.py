from django.db.models import IntegerChoices, TextChoices
from django.urls import reverse


class VocabularyNamespace(IntegerChoices):
    """
    A namespace for a vocabulary. HAWC will not enforce a single vocabulary, this can be controlled
    at the assessment level.
    """

    EHV = 1, "EHV"
    ToxRefDB = 2, "ToxRefDB"

    @classmethod
    def display_choices(cls) -> list:
        return [(item, item.display_name) for item in cls]

    @property
    def display_url(self) -> str:
        match self:
            case self.EHV:
                return reverse("vocab:ehv-browse")
            case self.ToxRefDB:
                return reverse("vocab:toxrefdb-browse")

    @property
    def display_name(self) -> str:
        match self:
            case self.EHV:
                return "EPA Environmental health vocabulary"
            case self.ToxRefDB:
                return "EPA ToxRefDB vocabulary"


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


class ObservationStatus(TextChoices):
    """
    Guideline profile observation status
    """

    NM = "NM", "NM"
    NR = "not required", "not required"
    RECOMMENDED = "recommended", "recommended"
    REQUIRED = "required", "required"
    TRIGGERED = "triggered", "triggered"
