from django.db import models
from django.urls import reverse

from ..common.models import IntChoiceEnum


class VocabularyNamespace(IntChoiceEnum):
    """
    A namespace for a vocabulary. HAWC will not enforce a single vocabulary, this can be controlled
    at the assessment level.
    """

    EHV = 1  # environmental health vocabulary


class VocabularyTermType(IntChoiceEnum):
    """
    Vocabulary will be associated with certain fields in HAWC. This enum allows us to map the vocab.
    """

    system = 1
    organ = 2
    effect = 3
    effect_subtype = 4
    endpoint_name = 5


class Term(models.Model):
    namespace = models.PositiveSmallIntegerField(
        choices=VocabularyNamespace.choices(), default=VocabularyNamespace.EHV
    )
    parent = models.ForeignKey("Term", on_delete=models.CASCADE, blank=True, null=True)
    type = models.PositiveIntegerField(choices=VocabularyTermType.choices())
    name = models.CharField(max_length=256)
    notes = models.TextField(blank=True)
    deprecated_on = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.get_namespace_display()}::{self.get_type_display()}::{self.name}"

    def get_admin_edit_url(self) -> str:
        return reverse("admin:vocab_term_change", args=(self.id,))


class Ontology(IntChoiceEnum):
    """
    Ontology for for UID
    """

    umls = 1


class Entity(models.Model):
    # mapping of controlled vocabulary to ontology
    ontology = models.PositiveSmallIntegerField(choices=Ontology.choices())
    uid = models.CharField(max_length=128, verbose_name="UID")
    terms = models.ManyToManyField(
        Term,
        through="EntityTermRelation",
        through_fields=("entity", "term"),
        related_name="entities",
    )
    deprecated_on = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "entities"
        unique_together = (("ontology", "uid"),)
        ordering = ("id",)

    def __str__(self) -> str:
        return self.uid

    def get_external_url(self) -> str:
        if self.ontology == Ontology.umls:
            return f"https://ncim.nci.nih.gov/ncimbrowser/pages/concept_details.jsf?dictionary=NCI%20Metathesaurus&code={self.uid}"
        else:
            raise ValueError("Unknown ontology type")


class EntityTermRelation(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, on_delete=models.PROTECT)
    deprecated_on = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.term} -> {self.entity}"
