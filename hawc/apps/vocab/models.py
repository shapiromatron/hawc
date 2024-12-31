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
    def vocab_dataframe(cls, namespace: constants.VocabularyNamespace) -> pd.DataFrame:
        dataframes = {
            constants.VocabularyNamespace.EHV: cls.ehv_dataframe,
            constants.VocabularyNamespace.ToxRefDB: cls.toxrefdb_dataframe,
        }
        return dataframes[namespace]()

    @classmethod
    def ehv_dataframe(cls) -> pd.DataFrame:
        vocab_data = cls.vocab_data(constants.VocabularyNamespace.EHV)
        term_data = [
            {"df": vocab_data["organ"], "left_on": "system_term_id"},
            {"df": vocab_data["effect"], "left_on": "organ_term_id"},
            {"df": vocab_data["effect_subtype"], "left_on": "effect_term_id"},
            {"df": vocab_data["endpoint_name"], "left_on": "effect_subtype_term_id"},
        ]
        df = cls.merge_data(vocab_data["system"], term_data)
        return df

    @classmethod
    def toxrefdb_dataframe(cls) -> pd.DataFrame:
        vocab_data = cls.vocab_data(constants.VocabularyNamespace.ToxRefDB)
        term_data = [
            {"df": vocab_data["effect"], "left_on": "system_term_id"},
            {"df": vocab_data["effect_subtype"], "left_on": "effect_term_id"},
            {"df": vocab_data["endpoint_name"], "left_on": "effect_subtype_term_id"},
        ]
        df = cls.merge_data(vocab_data["system"], term_data)
        return df

    @staticmethod
    def vocab_data(namespace) -> dict:
        cols = ("id", "type", "parent_id", "name")
        all_df = pd.DataFrame(
            data=list(
                Term.objects.filter(namespace=namespace, deprecated_on__isnull=True).values_list(
                    *cols
                )
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

        data = {
            "system": system_df,
            "organ": organ_df,
            "effect": effect_df,
            "effect_subtype": effect_subtype_df,
            "endpoint_name": endpoint_name_df,
        }

        return data

    @staticmethod
    def merge_data(df, data):
        # merge df queries based on relevant hierarchy
        for term in data:
            df = df.merge(term["df"], left_on=term["left_on"], right_on="parent_id").drop(
                columns=["parent_id"]
            )

        df = df.sort_values(by=[term["left_on"] for term in data]).reset_index(drop=True)
        return df

    def inheritance(self) -> dict:
        if self.namespace == constants.VocabularyNamespace.EHV:
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
        elif self.namespace == constants.VocabularyNamespace.ToxRefDB:
            return {
                "system": self.parent.parent.parent.name,
                "organ": None,
                "effect": self.parent.parent.name,
                "effect_subtype": self.parent.name,
                "name": self.name,
                "system_term_id": self.parent.parent.parent.id,
                "organ_term_id": None,
                "effect_term_id": self.parent.parent.id,
                "effect_subtype_term_id": self.parent.id,
                "name_term_id": self.id,
            }
        raise ValueError(f"Invalid namespace: {self.namespace}")


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


class GuidelineProfile(models.Model):
    objects = managers.GuidelineProfileManager()

    guideline_id = models.PositiveIntegerField()
    endpoint = models.ForeignKey("Term", on_delete=models.CASCADE, blank=True, null=True)
    obs_status = models.CharField(choices=constants.ObservationStatus, null=True)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        guideline_name = GuidelineProfile.objects.get_guideline_name(self.guideline_id)
        return f"{guideline_name}:{self.obs_status}"

    def get_admin_edit_url(self) -> str:
        return reverse("admin:vocab_guidelineprofile_change", args=(self.id,))


class Observation(models.Model):
    objects = managers.ObservationManager()

    experiment = models.ForeignKey(
        "animal.Experiment", on_delete=models.CASCADE, blank=True, null=True
    )
    endpoint = models.ForeignKey("Term", on_delete=models.CASCADE, blank=True, null=True)
    tested_status = models.BooleanField(default=False)
    reported_status = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.experiment}:{self.endpoint}"

    def get_assessment(self):
        return self.experiment.get_assessment()


reversion.register(Term)
reversion.register(Entity)
reversion.register(EntityTermRelation)
reversion.register(GuidelineProfile)
reversion.register(Observation)
