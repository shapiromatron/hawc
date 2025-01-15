import logging
import os

import pandas as pd
from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from django.http import Http404
from django.urls import reverse
from reversion import revisions as reversion

from ..assessment.models import Communication
from ..common.helper import SerializerHelper
from ..lit.models import Reference
from ..udf.models import ModelUDFContent
from . import constants, managers

logger = logging.getLogger(__name__)


class Study(Reference):
    objects = managers.StudyManager()

    TEXT_CLEANUP_FIELDS = (
        "short_citation",
        "full_citation",
        "study_identifier",
        "coi_details",
        "funding_source",
        "ask_author",
        "summary",
    )

    STUDY_TYPE_FIELDS = {
        "bioassay",
        "epi",
        "epi_meta",
        "in_vitro",
        "eco",
    }

    bioassay = models.BooleanField(
        verbose_name="Animal bioassay",
        default=False,
        help_text="Study contains animal bioassay data",
    )
    epi = models.BooleanField(
        verbose_name="Epidemiology",
        default=False,
        help_text="Study contains epidemiology data",
    )
    epi_meta = models.BooleanField(
        verbose_name="Epidemiology meta-analysis",
        default=False,
        help_text="Study contains epidemiology meta-analysis/pooled analysis data",
    )
    in_vitro = models.BooleanField(default=False, help_text="Study contains in-vitro data")
    eco = models.BooleanField(
        verbose_name="Ecology", default=False, help_text="Study contains ecology data"
    )
    short_citation = models.CharField(
        max_length=256,
        help_text="How the study should be identified (i.e. Smith et al. (2012), etc.)",
    )
    full_citation = models.TextField(help_text="Complete study citation, in desired format.")
    coi_reported = models.PositiveSmallIntegerField(
        choices=constants.CoiReported,
        default=constants.CoiReported.UNKNOWN,
        verbose_name="COI reported",
        help_text="Was a conflict of interest reported by the study authors?",
    )
    coi_details = models.TextField(
        blank=True,
        verbose_name="COI details",
        help_text="Details related to potential or disclosed conflict(s) of interest. "
        "When available, cut and paste the COI declaration with quotations. "
        "Provide details when a COI is inferred.",
    )
    funding_source = models.TextField(
        blank=True,
        help_text="When reported, cut and paste the funding source information with quotations, e.g., "
        + '"The study was sponsored by Hoechst AG and Dow Europe".',
    )
    study_identifier = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Internal study identifier",
        help_text="Reference descriptor for assessment-tracking purposes "
        '(for example, "{Author, year, #EndNoteNumber}")',
    )
    contact_author = models.BooleanField(
        default=False,
        help_text="Was the author contacted for clarification of methods, results, or to request additional data?",
    )
    ask_author = models.TextField(
        blank=True,
        verbose_name="Correspondence details",
        help_text="Details on correspondence between data-extractor and author (if author contacted). "
        "Redact confidential or personal information (e.g., email address).",
    )
    published = models.BooleanField(
        default=False,
        help_text="If True, this study, study evaluation, and extraction details may be visible "
        "to reviewers and/or the public (if assessment-permissions allow this level "
        "of visibility). Team-members and project-management can view both published "
        "and unpublished studies.",
    )
    summary = models.TextField(
        blank=True,
        verbose_name="Summary/extraction comments",
        help_text="This field is often left blank, but used to add comments on data extraction or other general comments. This field is displayed if an assessment is made public.",
    )
    editable = models.BooleanField(
        default=True,
        help_text="Project-managers and team-members are allowed to edit this study.",
    )

    udfs = GenericRelation(ModelUDFContent, related_query_name="studies")

    communications = GenericRelation(Communication, related_query_name="study_communications")

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        verbose_name_plural = "Studies"
        ordering = ("short_citation",)

    @classmethod
    def save_new_from_reference(cls, reference, attrs):
        """
        Save a new Study object from an existing reference object and the
        required information; difficult because of OneToOne relationship.

        Reference:
        https://github.com/lsaffre/lino/blob/master/lino/utils/mti.py
        """
        parent_link_field = Study._meta.parents.get(reference.__class__, None)
        attrs[parent_link_field.name] = reference
        for field in reference._meta.fields:
            attrs[field.name] = getattr(reference, field.name)
        # Set default citations
        if "full_citation" not in attrs:
            attrs["full_citation"] = reference.ref_full_citation
        if "short_citation" not in attrs:
            attrs["short_citation"] = reference.ref_short_citation
        internal_communications = attrs.pop("internal_communications", None)
        study = Study.objects.create(**attrs)
        if internal_communications and len(internal_communications.strip()) > 0:
            study.set_communications(internal_communications)
        return study

    @classmethod
    def metadata(cls) -> dict:
        # return schema metadata for choice fields
        return dict(coi_reported=dict(constants.CoiReported.choices))

    def __str__(self):
        return self.short_citation

    def get_absolute_url(self):
        return reverse("study:detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("study:update", args=[str(self.pk)])

    def get_final_rob_url(self):
        try:
            return self.get_final_rob().get_final_url()
        except ObjectDoesNotExist as err:
            raise Http404("Final RoB does not exist") from err

    def get_assessment(self):
        return self.assessment

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def get_attachments_dict(self) -> list[dict]:
        return [attachment.get_dict() for attachment in self.attachments.all()]

    def get_bioassay_endpoints(self):
        """
        Return a queryset of related bioassay endpoints for selected study
        """
        Endpoint = apps.get_model("animal", "Endpoint")
        Experiment = apps.get_model("animal", "Experiment")
        AnimalGroup = apps.get_model("animal", "AnimalGroup")

        if not self.bioassay:
            return Endpoint.objects.none()

        return Endpoint.objects.filter(
            animal_group__in=AnimalGroup.objects.filter(
                experiment__in=Experiment.objects.filter(study=self)
            )
        )

    def get_study_types(self) -> list[str]:
        types = []
        for field in self.STUDY_TYPE_FIELDS:
            if getattr(self, field):
                types.append(field)
        return types

    @classmethod
    def identifiers_df(cls, qs: models.QuerySet, relation: str) -> pd.DataFrame:
        """Returns a data frame with reference identifiers for each study in the QuerySet

        Args:
            qs (models.QuerySet): A QuerySet of an model with a relation to the study
            relation (str): The relation string to the `Study.study_id` for this QuerySet

        Returns:
            pd.DataFrame: A data frame an index of study/reference id, and columns for identifiers
        """
        study_ids = qs.values_list(relation, flat=True)
        studies = cls.objects.filter(id__in=study_ids)
        identifiers_df = Reference.objects.identifiers_dataframe(studies)
        return identifiers_df.set_index("reference_id")

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    def get_final_rob(self) -> models.Model:
        """
        Return the active, final risk of bias if one exists.

        Raises:
            ObjectDoesNotExist: If there is not one active final instance

        Returns:
            The active, final, RiskOfBias instance
        """
        try:
            return self.riskofbiases.get(final=True, active=True)
        except ObjectDoesNotExist as err:
            raise err
        except MultipleObjectsReturned as err:
            raise ObjectDoesNotExist(f'Multiple active final RoB "{self}", expecting one') from err

    def get_final_qs(self):
        return self.riskofbiases.filter(active=True, final=True).prefetch_related(
            "scores__overridden_objects__content_object"
        )

    def get_active_robs(self, with_final=True):
        if with_final:
            return (
                self.riskofbiases.filter(active=True)
                .order_by("final", "last_updated")
                .prefetch_related("author", "scores__overridden_objects__content_object")
            )
        else:
            return (
                self.riskofbiases.filter(active=True, final=False)
                .order_by("last_updated")
                .prefetch_related("author", "scores__overridden_objects__content_object")
            )

    def get_overall_confidence(self):
        # returns the overall RoB confidence score for a study, or -1 if none exists
        final_confidence_set = self.riskofbiases.prefetch_related("scores__metric__domain").filter(
            active=True, final=True, scores__metric__domain__is_overall_confidence=True
        )

        if final_confidence_set.exists():
            if final_confidence_set.count() != 1:
                return -1
            else:
                return final_confidence_set.values_list("scores__score", flat=True)[0]
        else:
            return -1

    def optimized_for_serialization(self):
        return (
            self.__class__.objects.filter(id=self.id)
            .prefetch_related(
                "identifiers",
                "searches",
                "riskofbiases__scores__metric__domain",
            )
            .first()
        )

    def get_study(self):
        return self

    def user_can_edit_study(self, assessment, user) -> bool:
        perms = assessment.get_permissions()
        return perms.can_edit_study(self, user)

    def get_communications(self) -> str:
        return Communication.get_message(self)

    def set_communications(self, text: str):
        Communication.set_message(self, text)

    def user_can_toggle_editable(self, user) -> bool:
        return self.assessment.user_is_project_manager_or_higher(user)

    def toggle_editable(self):
        self.editable = not self.editable
        self.save()

    def data_types(self) -> list[bool]:
        return [self.bioassay, self.epi, self.epi_meta, self.in_vitro, self.eco]

    @classmethod
    def delete_cache(cls, assessment_id: int, delete_reference_cache: bool = True):
        ids = list(cls.objects.filter(assessment_id=assessment_id).values_list("id", flat=True))
        SerializerHelper.delete_caches(cls, ids)
        if delete_reference_cache:
            apps.get_model("lit", "Reference").delete_cache(assessment_id, delete_study_cache=False)


class Attachment(models.Model):
    objects = managers.AttachmentManager()

    study = models.ForeignKey(Study, related_name="attachments", on_delete=models.CASCADE)
    attachment = models.FileField(upload_to="study-attachment")

    BREADCRUMB_PARENT = "study"

    def __str__(self):
        return self.filename

    def get_absolute_url(self):
        return reverse("study:attachment_detail", args=(self.pk,))

    def get_delete_url(self):
        return reverse("study:attachment_delete", args=[self.pk])

    @property
    def filename(self):
        return os.path.basename(self.attachment.name)

    def get_dict(self):
        return {
            "url": self.get_absolute_url(),
            "filename": self.filename,
            "url_delete": self.get_delete_url(),
        }

    def get_assessment(self):
        return self.study.assessment

    def get_study(self):
        return self.study


reversion.register(Study)
