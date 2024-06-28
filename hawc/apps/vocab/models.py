import pandas as pd
from django.db import models
from django.urls import reverse
from reversion import revisions as reversion

from ..myuser.models import HAWCUser
from . import constants, managers


class Term(models.Model):
    objects = managers.TermManager()

    uid = models.PositiveIntegerField(unique=True)
    namespace = models.PositiveSmallIntegerField(
        choices=constants.VocabularyNamespace, default=constants.VocabularyNamespace.EHV
    )
    parent = models.ForeignKey("Term", on_delete=models.CASCADE, blank=True, null=True)
    type = models.PositiveIntegerField(choices=constants.VocabularyTermType)
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
        names = dict(constants.VocabularyTermType.choices)
        all_df.loc[:, "type"] = all_df["type"].map(names)
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

    def ehv_endpoint_name(self) -> dict:
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

    @classmethod
    def toxref_dataframe(cls) -> pd.DataFrame:
        cols = ("id", "type", "parent_id", "name")
        all_df = pd.DataFrame(
            data=list(
                Term.objects.filter(namespace=2, deprecated_on__isnull=True).values_list(*cols)
            ),
            columns=cols,
        )
        names = dict(constants.VocabularyTermType.choices)
        all_df.loc[:, "type"] = all_df["type"].map(names)
        system_df = (
            all_df.query('type=="system"')
            .drop(columns=["type", "parent_id"])
            .rename(columns=dict(id="system_term_id", name="system"))
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
            system_df.merge(effect_df, left_on="system_term_id", right_on="parent_id")
            .drop(columns=["parent_id"])
            .merge(effect_subtype_df, left_on="effect_term_id", right_on="parent_id")
            .drop(columns=["parent_id"])
            .merge(endpoint_name_df, left_on="effect_subtype_term_id", right_on="parent_id")
            .drop(columns=["parent_id"])
            .sort_values(
                by=[
                    "system_term_id",
                    "effect_term_id",
                    "effect_subtype_term_id",
                    "name_term_id",
                ]
            )
            .reset_index(drop=True)
        )

        return df

    def toxref_endpoint_name(self) -> dict:
        return {
            "system": self.parent.parent.parent.name,
            "effect": self.parent.parent.name,
            "effect_subtype": self.parent.name,
            "name": self.name,
            "system_term_id": self.parent.parent.parent.id,
            "effect_term_id": self.parent.parent.id,
            "effect_subtype_term_id": self.parent.id,
            "name_term_id": self.id,
        }


class Entity(models.Model):
    # mapping of controlled vocabulary to ontology
    ontology = models.PositiveSmallIntegerField(choices=constants.Ontology)
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
        if self.ontology == constants.Ontology.umls:
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


reversion.register(Term)
reversion.register(Entity)
reversion.register(EntityTermRelation)
