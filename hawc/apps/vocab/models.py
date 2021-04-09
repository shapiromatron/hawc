from typing import Dict, List

import pandas as pd
from django.db import models
from django.urls import reverse
from django.utils.functional import classproperty
from reversion import revisions as reversion

from ..common.models import IntChoiceEnum
from ..myuser.models import HAWCUser
from . import managers


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


class Term(models.Model):
    objects = managers.TermManager()

    uid = models.PositiveIntegerField(unique=True, blank=True, null=True)
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

    @property
    def deprecated(self) -> bool:
        return self.deprecated_on is not None

    def get_admin_edit_url(self) -> str:
        return reverse("admin:vocab_term_change", args=(self.id,))

    @classmethod
    def ehv_dataframe(cls) -> pd.DataFrame:
        cols = ("id", "type", "parent_id", "name")
        all_df = pd.DataFrame(
            data=list(
                Term.objects.filter(namespace=1, deprecated_on__isnull=True).values_list(*cols)
            ),
            columns=cols,
        )
        all_df.loc[:, "type"] = all_df["type"].map(VocabularyTermType.as_dict())

        system_df = (
            all_df.query('type=="system"')
            .drop(columns=["type", "parent_id"])
            .rename(columns=dict(id="system_term_id", name="system"))
        )
        organ_df = (
            all_df.query('type=="organ"')
            .drop(columns=["type"])
            .rename(columns=dict(id="organ_term_id", name="organ"))
        )
        effect_df = (
            all_df.query('type=="effect"')
            .drop(columns=["type"])
            .rename(columns=dict(id="effect_term_id", name="effect"))
        )
        effect_subtype_df = (
            all_df.query('type=="effect_subtype"')
            .drop(columns=["type"])
            .rename(columns=dict(id="effect_subtype_term_id", name="effect_subtype"))
        )
        endpoint_name_df = (
            all_df.query('type=="endpoint_name"')
            .drop(columns=["type"])
            .rename(columns=dict(id="name_term_id", name="name"))
        )

        df = (
            system_df.merge(organ_df, left_on="system_term_id", right_on="parent_id")
            .drop(columns=["parent_id"])
            .merge(effect_df, left_on="organ_term_id", right_on="parent_id")
            .drop(columns=["parent_id"])
            .merge(effect_subtype_df, left_on="effect_term_id", right_on="parent_id")
            .drop(columns=["parent_id"])
            .merge(endpoint_name_df, left_on="effect_subtype_term_id", right_on="parent_id")
            .drop(columns=["parent_id"])
            .sort_values(
                by=[
                    "system_term_id",
                    "organ_term_id",
                    "effect_term_id",
                    "effect_subtype_term_id",
                    "name_term_id",
                ]
            )
            .reset_index(drop=True)
        )

        return df

    def ehv_endpoint_name(self) -> Dict:
        return {
            "system": self.parent.parent.parent.parent.name,
            "organ": self.parent.parent.parent.name,
            "effect": self.parent.parent.name,
            "effect_subtype": self.parent.name,
            "name": self.name,
            "system_term_id": self.parent.parent.parent.parent.id,
            "organ_term_id": self.parent.parent.parent.id,
            "effect_term_id": self.parent.parent.id,
            "effect_subtype_term_id": self.parent.id,
            "name_term_id": self.id,
        }


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
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(HAWCUser, blank=True, null=True, on_delete=models.CASCADE)
    approved_on = models.DateTimeField(blank=True, null=True)
    deprecated_on = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.term} -> {self.entity}"


class Comment(models.Model):
    commenter = models.ForeignKey(HAWCUser, on_delete=models.CASCADE)
    last_url_visited = models.CharField(max_length=128)
    comment = models.TextField()
    reviewed = models.BooleanField(default=False)
    reviewer_notes = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.commenter} on {self.created_on}"


reversion.register(Term)
reversion.register(Entity)
reversion.register(EntityTermRelation)
reversion.register(Comment)
