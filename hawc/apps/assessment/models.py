import json
import logging
import uuid
from collections import namedtuple
from typing import Any, NamedTuple

import numpy as np
import pandas as pd
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.http import HttpRequest
from django.template import RequestContext, Template
from django.template.defaultfilters import truncatewords
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from pydantic import BaseModel as PydanticModel
from reversion import revisions as reversion
from treebeard.mp_tree import MP_Node

from hawc.services.epa.dsstox import DssSubstance

from ..common.exceptions import AssessmentNotFound
from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper, cacheable, new_window_a
from ..common.models import AssessmentRootMixin, ColorField, get_private_data_storage
from ..common.validators import FlatJSON, validate_hyperlink
from ..materialized.models import refresh_all_mvs
from ..myuser.models import HAWCUser
from ..vocab.constants import VocabularyNamespace
from . import constants, jobs, managers
from .permissions import AssessmentPermissions
from .tasks import add_time_spent

logger = logging.getLogger(__name__)


class NoelNames(NamedTuple):
    noel: str
    loel: str
    noel_help_text: str
    loel_help_text: str


class DSSTox(models.Model):
    dtxsid = models.CharField(
        max_length=80,
        primary_key=True,
        verbose_name="DSSTox substance identifier (DTXSID)",
    )
    content = models.JSONField(default=dict)

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("dtxsid",)
        verbose_name = "DSSTox substance"
        verbose_name_plural = "DSSTox substances"

    def __str__(self):
        return self.dtxsid

    def save(self, *args, **kwargs):
        """
        Save the DSSTox to the database.

        Raises:
            ValueError if the supplied dtxsid isn't valid
        """
        if len(self.content) == 0:
            # If no content set, then attempt to set it based on the dtxsid.
            substance = DssSubstance.create_from_dtxsid(self.dtxsid)
            self.content = substance.content

        super().save(*args, **kwargs)

    @property
    def verbose_str(self) -> str:
        return f"{self.dtxsid}: {self.content['preferredName']} (CASRN {self.content['casrn']})"

    @property
    def verbose_link(self) -> str:
        return f"{new_window_a(self.get_dashboard_url(), self.dtxsid)}: {self.content['preferredName']} (CASRN {self.content['casrn']})"

    @classmethod
    def help_text(cls) -> str:
        return f'{new_window_a("https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database", "DssTox")} substance identifier (recommended). When using an identifier, chemical name and CASRN are standardized using the <a href="https://comptox.epa.gov/dashboard/" rel="noopener noreferrer" target="_blank">DTXSID</a>.'

    def get_dashboard_url(self) -> str:
        return f"https://comptox.epa.gov/dashboard/dsstoxdb/results?search={self.dtxsid}"

    def get_img_url(self) -> str:
        # TODO - always use api-ccte.epa.gov when API key is no longer required
        if not settings.CCTE_API_KEY:
            return f"https://comptox.epa.gov/dashboard-api/ccdapp1/chemical-files/image/by-dtxsid/{self.dtxsid}"
        else:
            return f"https://api-ccte.epa.gov/chemical/file/image/search/by-dtxsid/{self.dtxsid}?x-api-key={settings.CCTE_API_KEY}"


class Assessment(models.Model):
    objects = managers.AssessmentManager()

    def get_noel_name_default():
        if settings.HAWC_FLAVOR == "PRIME":
            return constants.NoelName.NOEL
        elif settings.HAWC_FLAVOR == "EPA":
            return constants.NoelName.NOAEL
        else:
            raise ValueError("Unknown HAWC flavor")

    def get_rob_name_default():
        if settings.HAWC_FLAVOR == "PRIME":
            return constants.RobName.ROB
        elif settings.HAWC_FLAVOR == "EPA":
            return constants.RobName.SE
        else:
            raise ValueError("Unknown HAWC flavor")

    name = models.CharField(
        max_length=80,
        verbose_name="Assessment Name",
        help_text="Describe the objective of the health-assessment.",
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Assessment Year",
        help_text="Year with which the assessment should be associated.",
    )
    version = models.CharField(
        max_length=80,
        verbose_name="Assessment Version",
        help_text="Version to describe the current assessment (i.e. draft, final, v1).",
    )
    cas = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Chemical identifier (CAS)",
        help_text="Add a single CAS-number if one is available to describe the "
        "assessment, otherwise leave-blank.",
    )
    dtxsids = models.ManyToManyField(
        DSSTox,
        blank=True,
        related_name="assessments",
        verbose_name="DSSTox substance identifiers (DTXSID)",
        help_text="""
        Related <a href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DSSTox</a>
        substance identifiers for this assessment.
        """,
    )
    assessment_objective = models.TextField(
        help_text="Describe the assessment objective(s), research questions, and purpose of this HAWC assessment. If a related peer-reviewed paper or journal article is available describing this work, please add a citation and hyperlink.",
    )
    authors = models.TextField(
        verbose_name="Assessment authors/organization",
        help_text="""A publicly visible description of the assessment authors (if the assessment is made public). This could be an organization, a group, or the individual scientists involved.""",
    )
    creator = models.ForeignKey(
        HAWCUser,
        null=True,
        related_name="created_assessments",
        on_delete=models.SET_NULL,
        editable=False,
    )
    project_manager = models.ManyToManyField(
        HAWCUser,
        related_name="assessment_pms",
        help_text="Has complete assessment control, including the ability to "
        "add team members, make public, or delete an assessment. "
        "You can add multiple project-managers.",
    )
    team_members = models.ManyToManyField(
        HAWCUser,
        related_name="assessment_teams",
        blank=True,
        help_text="Can view and edit assessment components, "
        "if project is editable. "
        "You can add multiple team-members",
    )
    reviewers = models.ManyToManyField(
        HAWCUser,
        related_name="assessment_reviewers",
        blank=True,
        help_text="Can view the assessment even if the assessment is not public, "
        "but cannot add or change content. You can add multiple reviewers.",
    )
    editable = models.BooleanField(
        default=True,
        help_text="Project-managers and team-members are allowed to edit assessment components.",
    )
    public_on = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Public",
        help_text="The assessment can be viewed by the general public.",
    )
    hide_from_public_page = models.BooleanField(
        default=False,
        help_text="If public, anyone with a link can view, "
        "but do not show a link on the public-assessment page.",
    )
    enable_literature_review = models.BooleanField(
        default=True,
        help_text="Search or import references from PubMed and other literature "
        "databases, define inclusion, exclusion, or descriptive tags, "
        "and apply these tags to retrieved literature for your analysis.",
    )
    enable_project_management = models.BooleanField(
        default=True,
        help_text="Enable project management module for data extraction and "
        "risk of bias. If enabled, each study will have multiple "
        "tasks which can be assigned and tracked for completion.",
    )
    enable_data_extraction = models.BooleanField(
        default=True,
        help_text="Extract animal bioassay, epidemiological, or in-vitro data from "
        "key references and create customizable, dynamic visualizations "
        "or summary data and associated metadata for display.",
    )
    enable_risk_of_bias = models.BooleanField(
        default=True,
        help_text="Define criteria for a systematic review of literature, and apply "
        "these criteria to references in your literature-review. "
        "View details on findings and identify areas with a potential "
        "risk of bias.",
    )
    enable_bmd = models.BooleanField(
        default=True,
        verbose_name="Enable BMD modeling",
        help_text="Conduct benchmark dose (BMD) modeling on animal bioassay data "
        "available in the HAWC database, using the US EPA's Benchmark "
        "Dose Modeling Software (BMDS).",
    )
    enable_summary_tables = models.BooleanField(
        default=True,
        help_text="Create summary tables of data and/or study evaluations extracted in HAWC, or build custom user defined tables. Show the summary tables link on the assessment sidebar.",
    )
    enable_visuals = models.BooleanField(
        default=True,
        help_text="Create visualizations of data and/or study evaluations extracted in HAWC, or using data uploaded from a tabular dataset. Show the visuals link on the assessment sidebar.",
    )
    enable_summary_text = models.BooleanField(
        default=True,
        help_text="Create custom-text to describe methodology and results of the "
        "assessment; insert tables, figures, and visualizations to using "
        '"smart-tags" which link to other data in HAWC.',
    )
    enable_downloads = models.BooleanField(
        default=True,
        help_text="Show the downloads link on the assessment sidebar.",
    )
    conflicts_of_interest = models.TextField(
        blank=True,
        help_text="Describe any conflicts of interest by the assessment-team.",
    )
    funding_source = models.TextField(
        blank=True, help_text="Describe the funding-source(s) for this assessment."
    )
    noel_name = models.PositiveSmallIntegerField(
        default=get_noel_name_default,
        choices=constants.NoelName,
        verbose_name="NEL/NOEL/NOAEL name",
        help_text="What term should be used to refer to NEL/NOEL/NOAEL and LEL/LOEL/LOAEL?",
    )
    rob_name = models.PositiveSmallIntegerField(
        default=get_rob_name_default,
        choices=constants.RobName,
        verbose_name="Risk of bias/Study evaluation name",
        help_text="What term should be used to refer to risk of bias/study evaluation questions?",
    )
    vocabulary = models.PositiveSmallIntegerField(
        choices=VocabularyNamespace.display_choices(),
        default=VocabularyNamespace.EHV,
        blank=True,
        null=True,
        verbose_name="Controlled vocabulary",
        help_text="""Attempt to use a controlled vocabulary for entering bioassay data into HAWC.
        You still have the option to enter terms which are not available in the vocabulary.""",
    )
    modify_uncontrolled_vocabulary = models.BooleanField(
        default=True,
        verbose_name="Curators can modify terms",
        help_text="""If using a controlled vocabulary and content is added which requires the
        definition of new terms, these may be modified and by curators who map new terms to the
        controlled vocabulary. Opting in means the values may change. It is recommended to select
        this option until you like to "freeze" your assessment, and then this can be unchecked, if
        needed.""",
    )
    epi_version = models.PositiveSmallIntegerField(
        choices=constants.EpiVersion,
        default=constants.EpiVersion.V2,
        verbose_name="Epidemiology schema version",
        help_text="Data extraction schema version used for epidemiology studies",
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Additional information about this assessment; only visible to HAWC admins",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = None

    def get_assessment(self):
        return self

    def get_absolute_url(self):
        return reverse("assessment:detail", args=(self.id,))

    def get_assessment_logs_url(self):
        return reverse("assessment:assessment_logs", args=(self.id,))

    def get_udf_list_url(self):
        return reverse("udf:binding-list", args=(self.id,))

    def get_clear_cache_url(self):
        return reverse("assessment:clear_cache", args=(self.id,))

    def get_details_form_url(self):
        return (
            reverse("assessment:details-update", args=(self.details.id,))
            if hasattr(self, "details")
            else reverse("assessment:details-create", args=(self.id,))
        )

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.name} ({self.year})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        AssessmentPermissions.clear_cache(self.id)

    def get_permissions(self) -> AssessmentPermissions:
        return AssessmentPermissions.get(self)

    def user_permissions(self, user):
        perms = self.get_permissions()
        return perms.to_dict(user)

    def user_can_view_object(self, user, perms: AssessmentPermissions | None = None) -> bool:
        # reviewer or higher OR assessment is public
        if perms is None:
            perms = self.get_permissions()
        return perms.can_view_object(user)

    def user_can_edit_object(self, user, perms: AssessmentPermissions | None = None) -> bool:
        # team member or higher AND assessment is editable
        if perms is None:
            perms = self.get_permissions()
        return perms.can_edit_object(user)

    def user_can_edit_assessment(self, user, perms: AssessmentPermissions | None = None) -> bool:
        if perms is None:
            perms = self.get_permissions()
        return perms.project_manager_or_higher(user)

    def user_is_reviewer_or_higher(self, user) -> bool:
        perms = self.get_permissions()
        return perms.reviewer_or_higher(user)

    def user_is_team_member_or_higher(self, user) -> bool:
        perms = self.get_permissions()
        return perms.team_member_or_higher(user)

    def user_is_project_manager_or_higher(self, user) -> bool:
        perms = self.get_permissions()
        return perms.project_manager_or_higher(user)

    def get_vocabulary_display(self) -> str:
        # override default method
        if self.vocabulary:
            return VocabularyNamespace(self.vocabulary).display_name
        else:
            return ""

    def get_noel_names(self) -> NoelNames:
        if self.noel_name == constants.NoelName.NEL:
            return NoelNames(
                "NEL",
                "LEL",
                "No effect level",
                "Lowest effect level",
            )
        elif self.noel_name == constants.NoelName.NOEL:
            return NoelNames(
                "NOEL",
                "LOEL",
                "No observed effect level",
                "Lowest observed effect level",
            )
        elif self.noel_name == constants.NoelName.NOAEL:
            return NoelNames(
                "NOAEL",
                "LOAEL",
                "No observed adverse effect level",
                "Lowest observed adverse effect level",
            )
        else:
            raise ValueError(f"Unknown noel_name: {self.noel_name}")

    def bust_cache(self):
        """
        Delete the cache for all objects in an assessment; look for all cases
        where `SerializerHelper.get_serialized` is used.
        """
        for Model, filters in [
            (apps.get_model("animal", "Endpoint"), dict(assessment_id=self.id)),
            (apps.get_model("epi", "Outcome"), dict(assessment_id=self.id)),
            (
                apps.get_model("epimeta", "MetaProtocol"),
                dict(study__assessment_id=self.id),
            ),
            (
                apps.get_model("epimeta", "MetaResult"),
                dict(protocol__study__assessment_id=self.id),
            ),
            (apps.get_model("invitro", "IVEndpoint"), dict(assessment_id=self.id)),
            (apps.get_model("mgmt", "Task"), dict(study__assessment_id=self.id)),
            (
                apps.get_model("riskofbias", "RiskOfBias"),
                dict(study__assessment_id=self.id),
            ),
            (apps.get_model("summary", "Visual"), dict(assessment_id=self.id)),
        ]:
            ids = list(Model.objects.filter(**filters).values_list("id", flat=True))
            SerializerHelper.delete_caches(Model, ids)

        apps.get_model("study", "Study").delete_cache(self.id)

        try:
            # django-redis can delete by key pattern
            cache.delete_pattern(f"assessment-{self.id}-*")
        except AttributeError:
            if settings.DEBUG or settings.IS_TESTING:
                # if debug/testing, wipe whole cache
                cache.clear()
            else:
                # in prod, throw exception
                raise NotImplementedError("Cannot wipe assessment cache using this cache backend")

        # refresh materialized views
        refresh_all_mvs(force=True)

    def pms_and_team_users(self) -> models.QuerySet:
        # return users that are either project managers or team members
        return (
            HAWCUser.objects.filter(
                models.Q(assessment_pms=self.id) | models.Q(assessment_teams=self.id)
            )
            .order_by("last_name", "id")
            .distinct("id", "last_name")
        )

    def get_communications(self) -> str:
        return Communication.get_message(self)

    def set_communications(self, text: str):
        Communication.set_message(self, text)

    def _has_data(self, app: str, model: str, filter: str = "study__assessment") -> bool:
        """Check if associated model has any data for this assessment in HAWC

        Args:
            app (str): the application name
            model (str): the model name
            filter (str): the filter to apply to check for status

        Returns:
            bool: True if data exists, False otherwise
        """
        return apps.get_model(app, model).objects.filter(**{filter: self}).count() > 0

    @property
    def has_lit_data(self) -> bool:
        return self._has_data("lit", "Reference", filter="assessment")

    @property
    def has_rob_data(self) -> bool:
        return self._has_data("riskofbias", "RiskOfBias")

    @property
    def has_animal_data(self) -> bool:
        return self._has_data("animal", "Experiment")

    @property
    def has_epi_data(self) -> bool:
        if self.epi_version == constants.EpiVersion.V1:
            return self._has_data("epi", "StudyPopulation")
        elif self.epi_version == constants.EpiVersion.V2:
            return self._has_data("epiv2", "Design")
        else:
            raise ValueError("Unknown epi version")

    @property
    def has_epimeta_data(self) -> bool:
        return self._has_data("epimeta", "MetaProtocol")

    @property
    def has_invitro_data(self) -> bool:
        return self._has_data("invitro", "IVExperiment")

    @property
    def has_eco_data(self) -> bool:
        return self._has_data("eco", "Design")


class AssessmentDetail(models.Model):
    objects = managers.AssessmentDetailManager()
    assessment = models.OneToOneField(Assessment, models.CASCADE, related_name="details")
    project_type = models.CharField(
        max_length=64,
        blank=True,
        help_text="If part of a product line, the name of the project type",
    )
    project_status = models.PositiveSmallIntegerField(
        choices=constants.Status,
        default=constants.Status.SCOPING,
        help_text="High-level project management milestones for this assessment",
    )
    project_url = models.URLField(
        blank=True,
        validators=[validate_hyperlink],
        verbose_name="External Project URL",
        help_text="The URL to an external project page, if one exists",
    )
    peer_review_status = models.PositiveSmallIntegerField(
        verbose_name="Peer Review Status",
        choices=constants.PeerReviewType,
        help_text="Define the current status of peer review of this assessment, if any",
        default=constants.PeerReviewType.NONE,
    )
    qa_id = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Quality Assurance (QA) tracking identifier",
        help_text="Quality Assurance (QA) tracking identifier, if one exists.",
    )
    qa_url = models.URLField(
        blank=True,
        verbose_name="Quality Assurance (QA) URL",
        help_text="Quality Assurance Website, if any",
        validators=[validate_hyperlink],
    )
    report_id = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Report identifier",
        help_text="A external report number or identifier (e.g., a DOI, publication number)",
    )
    report_url = models.URLField(
        blank=True,
        validators=[validate_hyperlink],
        verbose_name="External Document URL",
        help_text="The URL to the final document or publication, if one exists",
    )
    extra = models.JSONField(
        default=dict,
        validators=[FlatJSON.validate],
        blank=True,
        verbose_name="Additional fields",
        help_text="Any additional custom fields; " + FlatJSON.HELP_TEXT,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    def __str__(self):
        return f"{self.assessment}: Details"

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse("assessment:detail", args=(self.assessment_id,))

    def get_peer_review_status_display(self) -> str:
        value = constants.PeerReviewType(self.peer_review_status)
        if value.display():
            return value.label
        return ""


class AssessmentValue(models.Model):
    objects = managers.AssessmentValueManager()

    assessment = models.ForeignKey(Assessment, models.CASCADE, related_name="values")
    evaluation_type = models.PositiveSmallIntegerField(
        choices=constants.EvaluationType,
        default=constants.EvaluationType.CANCER,
        help_text="Substance evaluation conducted",
    )
    system = models.CharField(
        verbose_name="System or health effect basis",
        max_length=128,
        help_text="Identify the health system of concern (e.g., Hepatic, Nervous, Reproductive)",
    )
    value_type = models.PositiveSmallIntegerField(
        choices=constants.ValueType,
        help_text="Type of derived value",
    )
    value = models.FloatField(
        help_text="The derived value",
    )
    value_unit = models.CharField(verbose_name="Value units", max_length=32)
    adaf = models.BooleanField(
        verbose_name="Apply ADAF?",
        default=False,
        help_text="When checked, the ADAF note will appear as a footnote for the value. Add supporting information about ADAF in the comments.",
    )
    confidence = models.CharField(
        max_length=64,
        blank=True,
        help_text="Confidence in the toxicity value",
    )
    duration = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Value duration",
        help_text="Duration associated with the value (e.g., Chronic, Subchronic)",
    )
    basis = models.TextField(
        blank=True,
        help_text="Describe the justification for deriving this value. Information should include the endpoint of concern from the principal study (e.g., decreased embryo/fetal survival) with the appropriate references included (Smith et al. 2023)",
    )
    pod_type = models.CharField(
        verbose_name="POD Type",
        max_length=32,
        blank=True,
        help_text="Point of departure type, for example, NOAEL, LOAEL, BMDL (10% extra risk)",
    )
    pod_value = models.FloatField(
        verbose_name="POD Value",
        blank=True,
        null=True,
        help_text="The Point of Departure (POD)",
    )
    pod_unit = models.CharField(
        verbose_name="POD units",
        max_length=32,
        blank=True,
        help_text="Units for the Point of Departure (POD)",
    )
    uncertainty = models.IntegerField(
        blank=True,
        null=True,
        choices=constants.UncertaintyChoices,
        verbose_name="Uncertainty factor",
        help_text="Composite uncertainty factor applied to POD to derive the final value",
    )
    species_studied = models.TextField(
        blank=True,
        verbose_name="Species and strain",
        help_text="Provide information about the animal(s) studied, including species and strain information",
    )
    study = models.ForeignKey(
        "study.Study",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Key study",
        help_text="Link to Key Study in HAWC. If it does not exist or there are multiple studies, leave blank and explain in comments",
    )
    evidence = models.TextField(
        verbose_name="Evidence characterization",
        blank=True,
        help_text="Describe the overall characterization of the evidence (e.g., cancer or noncancer descriptors) and the basis for this determination (e.g., based on strong and consistent evidence in animals and humans)",
    )
    tumor_type = models.CharField(
        max_length=128,
        verbose_name="Tumor/Cancer type",
        blank=True,
        help_text="Describe the specific types of cancer found within the specific organ system (e.g., tumor site)",
    )
    extrapolation_method = models.TextField(
        blank=True,
        help_text="Describe the statistical method(s) used to derive the cancer toxicity values (e.g., Time-to-tumor dose-response model with linear extrapolation from the POD (BMDL10(HED)) associated with 10% extra cancer risk)",
    )
    comments = models.TextField(
        blank=True, help_text="General comments related to the derivation of this value"
    )
    extra = models.JSONField(
        default=dict,
        blank=True,
        validators=[FlatJSON.validate],
        verbose_name="Additional fields",
        help_text="Any additional custom fields; " + FlatJSON.HELP_TEXT,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        verbose_name_plural = "values"

    @property
    def show_cancer_fields(self):
        return self.evaluation_type in [
            constants.EvaluationType.CANCER,
            constants.EvaluationType.BOTH,
        ]

    @property
    def show_noncancer_fields(self):
        return self.evaluation_type in [
            constants.EvaluationType.NONCANCER,
            constants.EvaluationType.BOTH,
        ]

    def __str__(self):
        return f"Values for {self.assessment}"

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse("assessment:values-detail", args=[self.pk])

    @cached_property
    def check_calculated_value(self, rtol: float = 0.01) -> NamedTuple:
        # check if calculated value is different than reported value
        check = namedtuple("check", ["show_warning", "calculated_value", "tolerance"])
        if self.value and self.pod_value and self.uncertainty and self.uncertainty > 0:
            calculated = self.pod_value / self.uncertainty
            if not np.isclose(self.value, calculated, rtol=rtol):
                return check(True, calculated, rtol)
        return check(False, 0, rtol)


class Attachment(models.Model):
    objects = managers.AttachmentManager()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey("content_type", "object_id")
    title = models.CharField(max_length=128)
    attachment = models.FileField(upload_to="attachment")
    publicly_available = models.BooleanField(default=True)
    description = models.TextField()

    BREADCRUMB_PARENT = "content_object"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("assessment:attachment-htmx", args=[self.pk, "read"])

    def get_edit_url(self):
        return reverse("assessment:attachment-htmx", args=[self.pk, "update"])

    def get_delete_url(self):
        return reverse("assessment:attachment-htmx", args=[self.pk, "delete"])

    def get_dict(self):
        return {
            "url": self.get_absolute_url(),
            "url_delete": self.get_delete_url(),
            "url_update": self.get_update_url(),
            "title": self.title,
            "description": self.description,
        }

    def get_assessment(self):
        if self.content_object is None:
            raise AssessmentNotFound()
        return self.content_object.get_assessment()


class DoseUnits(models.Model):
    objects = managers.DoseUnitManager()

    name = models.CharField(max_length=20, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "dose units"
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def animal_dose_group_count(self):
        return self.dosegroup_set.count()

    @property
    def epi_exposure_count(self):
        return self.exposure_set.count()

    @property
    def invitro_experiment_count(self):
        return self.ivexperiments.count()


class Species(models.Model):
    objects = managers.SpeciesManager()

    name = models.CharField(
        max_length=30,
        help_text="Enter species in singular (ex: Mouse, not Mice)",
        unique=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "species"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Strain(models.Model):
    objects = managers.StrainManager()

    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("species", "name"),)
        ordering = ("species", "name")

    def __str__(self):
        return self.name


class EffectTag(models.Model):
    objects = managers.EffectTagManager()

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(
        max_length=128,
        unique=True,
        help_text="The URL (web address) used to describe this object (no spaces or special-characters).",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_json(self, json_encode=False):
        d = {}
        fields = ("pk", "name")
        for field in fields:
            d[field] = getattr(self, field)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @staticmethod
    def get_name_list(queryset):
        return "|".join(queryset.values_list("name", flat=True))


class BaseEndpoint(models.Model):
    """
    Parent quasi-abstract model for animal bioassay, epidemiology, or
    in-vitro endpoints used in assessment. Not fully abstract so efficient
    queries can pull data from all three more-specific endpoint types.
    """

    objects = managers.BaseEndpointManager()

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, db_index=True)
    # Some denormalization but required for efficient capture of all endpoints
    # in assessment; major use case in HAWC.

    name = models.CharField(max_length=128, verbose_name="Endpoint/Adverse outcome")
    effects = models.ManyToManyField(EffectTag, blank=True, verbose_name="Tags")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.assessment

    def get_json(self, *args, **kwargs):
        """
        Use the appropriate child-class to generate JSON response object, or
        return an empty object.
        """
        d = {}
        if hasattr(self, "outcome"):
            d = self.outcome.get_json(*args, **kwargs)
        elif hasattr(self, "endpoint"):
            d = self.endpoint.get_json(*args, **kwargs)
        elif hasattr(self, "ivendpoint"):
            d = self.ivendpoint.get_json(*args, **kwargs)
        return d


class TimeSpentEditing(models.Model):
    objects = managers.TimeSpentEditingManager()

    seconds = models.FloatField()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Time spent editing models"

    def __str__(self):
        return f"{self.content_type.model} {self.object_id}: {self.seconds/60:.1f} min"

    @classmethod
    def get_cache_name(cls, url, session_key):
        return str(hash(f"{url}-{session_key}"))

    @classmethod
    def set_start_time(cls, request: HttpRequest):
        cache_name = cls.get_cache_name(request.path, request.session.session_key)
        now = timezone.now()
        # Set max time of one hour on a page; otherwise assume the page is
        # open but user is doing other things.
        cache.set(cache_name, now, 60 * 60 * 1)

    @classmethod
    def add_time_spent_job(
        cls, request: HttpRequest, obj, assessment_id: int, url: str | None = None
    ):
        cache_name = cls.get_cache_name(url or request.path, request.session.session_key)
        content_type_id = ContentType.objects.get_for_model(obj).id
        # wait 10 seconds to make sure database is populated
        add_time_spent.s(cache_name, obj.id, assessment_id, content_type_id).apply_async(
            countdown=10
        )

    @classmethod
    def add_time_spent(cls, cache_name, object_id, assessment_id, content_type_id):
        time_spent, created = cls.objects.get_or_create(
            content_type_id=content_type_id,
            object_id=object_id,
            assessment_id=assessment_id,
            defaults={"seconds": 0},
        )

        now = timezone.now()
        start_time = cache.get(cache_name)
        if start_time:
            seconds_spent = now - start_time
            time_spent.seconds += seconds_spent.total_seconds()
            time_spent.save()
            cache.delete(cache_name)


class Dataset(models.Model):
    """
    An external Dataset
    """

    objects = managers.DatasetManager()

    assessment = models.ForeignKey(
        Assessment, editable=False, related_name="datasets", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    published = models.BooleanField(
        default=False,
        help_text="If True, this dataset may be visible to reviewers and/or the public "
        "(if assessment-permissions allow this level of visibility). Team-members and "
        "project-management can view both published and unpublished datasets.",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    VALID_EXTENSIONS = {".xlsx", ".csv", ".tsv"}
    BREADCRUMB_PARENT = "assessment"

    class Meta:
        ordering = ("created",)
        unique_together = (("assessment", "name"),)

    def __str__(self) -> str:
        return self.name

    def user_can_view(self, user) -> bool:
        return (
            self.published
            and self.assessment.user_can_view_object(user)
            or self.assessment.user_can_edit_object(user)
        )

    def get_absolute_url(self) -> str:
        return reverse("assessment:dataset_detail", args=(self.id,))

    def get_edit_url(self) -> str:
        return reverse("assessment:dataset_update", args=(self.id,))

    def get_delete_url(self) -> str:
        return reverse("assessment:dataset_delete", args=(self.id,))

    def get_assessment(self) -> Assessment:
        return self.assessment

    def get_api_detail_url(self) -> str:
        return reverse("assessment:api:dataset-detail", args=(self.id,))

    def get_api_data_url(self) -> str:
        return reverse("assessment:api:dataset-data", args=(self.id,))

    def get_latest_revision(self) -> "DatasetRevision":
        return self.revisions.latest()

    def get_new_version_value(self) -> int:
        try:
            return self.get_latest_revision().version + 1
        except (ValueError, models.ObjectDoesNotExist):
            return 1

    def get_latest_df(self) -> pd.DataFrame:
        return self.get_latest_revision().get_df()


class DatasetRevision(models.Model):
    """
    A specific external dataset revision
    """

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="revisions")
    version = models.PositiveSmallIntegerField(
        help_text="""The uploaded file is versioned; this is the version of the dataset currently
            being edited.""",
    )
    data = models.FileField(
        upload_to="assessment/dataset-revision",
        storage=get_private_data_storage(),
        help_text=f"""Upload a dataset ({", ".join(sorted(Dataset.VALID_EXTENSIONS))}).
            Dataset versions cannot be deleted, but if users are not team members, only the most
            recent dataset version will be visible. Visualizations using a dataset will use the
            latest version available.""",
    )
    metadata = models.JSONField(default=dict, editable=False)
    excel_worksheet_name = models.CharField(
        help_text="Worksheet name to use in Excel file. If blank, the first worksheet is used.",
        max_length=64,
        blank=True,
    )
    notes = models.TextField(
        blank=True,
        help_text="""Notes on specific revision. For example, describe what's different from a
            previous version. After save, cannot be edited.""",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created",)
        get_latest_by = "created"
        unique_together = (("dataset", "version"),)

    class Metadata(PydanticModel):
        filename: str
        extension: str
        num_rows: int
        num_columns: int
        column_names: list[str]

    def __str__(self) -> str:
        return f"{self.dataset}: v{self.version}"

    def get_api_data_url(self) -> str:
        return reverse("assessment:api:dataset-version", args=(self.dataset_id, self.version))

    def get_df(self) -> pd.DataFrame:
        return self.try_read_df(self.data, self.metadata["extension"], self.excel_worksheet_name)

    def data_exists(self) -> bool:
        try:
            _ = self.data.file
            return True
        except FileNotFoundError:
            logger.error(f"DatasetRevision {self.id} not found: {self.data.path}")
            return False

    @classmethod
    def try_read_df(cls, data, suffix: str, worksheet_name: str | None = None) -> pd.DataFrame:
        """
        Try to load and return a pandas dataframe.

        Args:
            data: File-like object
            suffix: str = File suffix
            worksheet_name: Optional[str] = Excel worksheet name, or empty string

        Returns:
            pd.DataFrame or throws a ValueError exception
        """
        kwargs = {}
        if suffix == ".xlsx":
            func = pd.read_excel
            if worksheet_name:
                kwargs["sheet_name"] = worksheet_name
        elif suffix in [".csv", ".tsv"]:
            func = pd.read_csv
            if suffix == ".tsv":
                kwargs["sep"] = "\t"
        else:
            raise ValueError(f"Unknown suffix: {suffix}")

        try:
            df = func(data.file, **kwargs)
        except Exception:
            raise ValueError("Unable load dataframe")

        if df.shape[0] == 0:
            raise ValueError("Dataframe contains no rows")

        if df.shape[1] == 0:
            raise ValueError("Dataframe contains no columns")

        return df


class Job(models.Model):
    JOB_TO_FUNC = {
        constants.JobType.TEST: jobs.test,
    }

    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(
        Assessment, blank=True, null=True, on_delete=models.CASCADE, related_name="jobs"
    )
    status = models.PositiveSmallIntegerField(
        choices=constants.JobStatus, default=constants.JobStatus.PENDING, editable=False
    )
    job = models.PositiveSmallIntegerField(
        choices=constants.JobType, default=constants.JobType.TEST
    )

    kwargs = models.JSONField(default=dict, blank=True, null=True)
    result = models.JSONField(default=dict, editable=False)

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    def execute(self) -> Any:
        """
        Executes the job. Function and kwargs are determined
        by the instance's "job" and "kwargs" properties, respectively.

        Returns:
            Any: Any data returned by the function call.
            {"data" : <return_value>} MUST be JSON serializable.
        """
        func = self.JOB_TO_FUNC[self.job]
        return func(**self.kwargs)

    def set_success(self, data):
        """
        Sets the status of the job to SUCCESS and sets the
        data as the job's result, in the format:
            {"data" : <data>}

        Args:
            data (Any): Data to be saved as the job's result.
            {"data" : <data>} MUST be JSON serializable.
        """
        self.result = {"data": data}
        self.status = constants.JobStatus.SUCCESS

    def set_failure(self, exception: Exception):
        """
        Sets the status of the job to FAILURE and sets the
        exception as the job's result, in the format:
            {"error" : <exception>}

        Args:
            exception (Exception): Exception to be saved as the job's result.
            MUST have a built in string representation.
        """
        self.result = {"error": str(exception)}
        self.status = constants.JobStatus.FAILURE


class Communication(models.Model):
    message = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("content_type_id", "object_id"),)

    @classmethod
    def get_message(cls, model) -> str:
        instance = cls.objects.filter(
            content_type=ContentType.objects.get_for_model(model), object_id=model.id
        ).first()
        return instance.message if instance else ""

    @classmethod
    def set_message(cls, model, text: str) -> "Communication":
        instance, _ = cls.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(model),
            object_id=model.id,
            defaults={"message": text},
        )
        return instance


class Log(models.Model):
    objects = managers.LogManager()

    assessment = models.ForeignKey(
        Assessment, blank=True, null=True, related_name="logs", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        HAWCUser, blank=True, null=True, related_name="logs", on_delete=models.SET_NULL
    )
    message = models.TextField()
    content = models.JSONField(default=dict)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.DO_NOTHING)
    object_id = models.IntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        if self.object_id and self.content_type_id:
            return self.get_object_name() + " Log"
        if self.assessment is not None:
            return str(self.assessment) + " Log"
        return "Custom Log"

    def get_absolute_url(self):
        return reverse("assessment:log_detail", args=(self.id,))

    def get_object_list_url(self):
        return reverse("assessment:log_object_list", args=(self.content_type_id, self.object_id))

    def get_object_url(self):
        # get list view if we can, else fall-back to the absolute view
        if self.object_id and self.content_type_id:
            return self.get_object_list_url()
        return self.get_absolute_url()

    def get_assessment(self):
        return self.assessment

    def get_generic_object_name(self) -> str:
        return f"{self.content_type.app_label}.{self.content_type.model} #{self.object_id}"

    def get_object_name(self):
        if self.content_object:
            return str(self.content_object)
        if self.object_id and self.content_type_id:
            return self.get_generic_object_name()

    def user_can_view(self, user) -> bool:
        return (
            self.assessment.user_is_team_member_or_higher(user)
            if self.assessment
            else user.is_staff
        )


class ContentTypeChoices(models.IntegerChoices):
    HOMEPAGE = 1
    ABOUT = 2
    RESOURCES = 3


class Content(models.Model):
    content_type = models.PositiveIntegerField(choices=ContentTypeChoices, unique=True)
    template = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        return self.get_content_type_display()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.clear_cache()

    def clear_cache(self):
        key = self.get_cache_key(self.content_type)
        cache.delete(key)

    @property
    def template_truncated(self):
        return truncatewords(self.template, 100)

    @classmethod
    def get_cache_key(cls, content_type: ContentTypeChoices) -> str:
        return f"assessment.Content.{content_type}"

    @classmethod
    def rendered_page(
        cls, content_type: ContentTypeChoices, request: HttpRequest, context: dict
    ) -> str:
        """Return rendered template response for the requested content.

        Return cached content for this page if one exists, or if it does not exist, render using
        the current context provided, cache, and return.
        """
        key = cls.get_cache_key(content_type)
        context = RequestContext(request, context)
        content = cls.objects.get(content_type=content_type)
        html = Template(content.template).render(context)
        cache_html = cacheable(lambda: html, key, cache_duration=settings.CACHE_10_MIN)
        return cache_html


class Tag(AssessmentRootMixin, MP_Node):
    objects = managers.TagManager()

    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    color = ColorField(default="#ffffff")
    assessment = models.ForeignKey(Assessment, models.CASCADE, related_name="tags")
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    cache_template_taglist = "assessment.tag.taglist.assessment-{0}"
    cache_template_tagtree = "assessment.tag.tagtree.assessment-{0}"

    @classmethod
    def create_root(cls, assessment_id, **kwargs):
        """
        Constructor to define root with assessment-creation
        """
        kwargs["name"] = cls.get_assessment_root_name(assessment_id)
        kwargs["assessment_id"] = assessment_id
        return cls.add_root(**kwargs)

    def get_nested_name(self) -> str:
        if self.is_root():
            return "<root-node>"
        else:
            return f"{'━ ' * (self.depth - 1)}{self.name}"

    def get_absolute_url(self):
        return reverse("assessment:tag-htmx", args=[self.pk, "read"])

    def get_edit_url(self):
        return reverse("assessment:tag-htmx", args=[self.pk, "update"])

    def get_delete_url(self):
        return reverse("assessment:tag-htmx", args=[self.pk, "delete"])


class TaggedItem(models.Model):
    tag = models.ForeignKey(Tag, models.CASCADE, related_name="items")
    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


reversion.register(DSSTox)
reversion.register(Assessment)
reversion.register(AssessmentDetail)
reversion.register(AssessmentValue)
reversion.register(Attachment)
reversion.register(EffectTag)
reversion.register(Species)
reversion.register(Strain)
reversion.register(BaseEndpoint)
reversion.register(Dataset)
reversion.register(DatasetRevision)
reversion.register(Job)
reversion.register(Communication)
reversion.register(Content)
