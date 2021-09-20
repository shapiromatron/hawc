import json
import logging
import uuid
from typing import Any, Dict, List, NamedTuple

import pandas as pd
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.validators import MinValueValidator
from django.db import models
from django.http import HttpRequest
from django.template import RequestContext, Template
from django.template.defaultfilters import truncatewords
from django.urls import reverse
from django.utils import timezone
from pydantic import BaseModel as PydanticModel
from reversion import revisions as reversion

from hawc.services.epa.dsstox import DssSubstance

from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper, read_excel
from ..common.models import IntChoiceEnum, get_private_data_storage
from ..materialized.models import refresh_all_mvs
from ..myuser.models import HAWCUser
from ..vocab.models import VocabularyNamespace
from . import jobs, managers
from .permissions import AssessmentPermissions
from .tasks import add_time_spent

logger = logging.getLogger(__name__)

NOEL_NAME_CHOICES_NOEL = 0
NOEL_NAME_CHOICES_NOAEL = 1
NOEL_NAME_CHOICES_NEL = 2

ROB_NAME_CHOICES_ROB = 0
ROB_NAME_CHOICES_SE = 1
ROB_NAME_CHOICES_ROB_TEXT = "Risk of bias"
ROB_NAME_CHOICES_SE_TEXT = "Study evaluation"


class NoelNames(NamedTuple):
    noel: str
    loel: str
    noel_help_text: str
    loel_help_text: str


class JobStatus(IntChoiceEnum):
    """
    Status of the running job.
    """

    PENDING = 1
    SUCCESS = 2
    FAILURE = 3


class JobType(IntChoiceEnum):
    """
    Short descriptor of job functionality.
    """

    TEST = 1


class DSSTox(models.Model):
    dtxsid = models.CharField(
        max_length=80, primary_key=True, verbose_name="DSSTox substance identifier (DTXSID)",
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
        return f"<a href={self.get_dashboard_url()}>{self.dtxsid}</a>: {self.content['preferredName']} (CASRN {self.content['casrn']})"

    def get_dashboard_url(self) -> str:
        return f"https://comptox.epa.gov/dashboard/dsstoxdb/results?search={self.dtxsid}"

    def get_svg_url(self) -> str:
        return f"https://actorws.epa.gov/actorws/chemical/image?dtxsid={self.dtxsid}&fmt=svg"


class Assessment(models.Model):
    objects = managers.AssessmentManager()

    NOEL_NAME_CHOICES = (
        (NOEL_NAME_CHOICES_NEL, "NEL/LEL"),
        (NOEL_NAME_CHOICES_NOEL, "NOEL/LOEL"),
        (NOEL_NAME_CHOICES_NOAEL, "NOAEL/LOAEL"),
    )

    ROB_NAME_CHOICES = (
        (ROB_NAME_CHOICES_ROB, ROB_NAME_CHOICES_ROB_TEXT),
        (ROB_NAME_CHOICES_SE, ROB_NAME_CHOICES_SE_TEXT),
    )

    def get_noel_name_default():
        if settings.HAWC_FLAVOR == "PRIME":
            return NOEL_NAME_CHOICES_NOEL
        elif settings.HAWC_FLAVOR == "EPA":
            return NOEL_NAME_CHOICES_NOAEL
        else:
            raise ValueError("Unknown HAWC flavor")

    def get_rob_name_default():
        if settings.HAWC_FLAVOR == "PRIME":
            return ROB_NAME_CHOICES_ROB
        elif settings.HAWC_FLAVOR == "EPA":
            return ROB_NAME_CHOICES_SE
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
        blank=True,
        help_text="Describe the assessment objective(s), research questions, "
        "or clarification on the purpose of the assessment.",
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
    public = models.BooleanField(
        default=False, help_text="The assessment can be viewed by the general public."
    )
    hide_from_public_page = models.BooleanField(
        default=False,
        help_text="If public, anyone with a link can view, "
        "but do not show a link on the public-assessment page.",
    )
    is_public_training_data = models.BooleanField(
        default=False,
        verbose_name="Public training data",
        help_text="Allows data to be anonymized and made available for machine learning projects. Both assessment ID and user ID will be made anonymous for these purposes.",
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
    enable_summary_text = models.BooleanField(
        default=True,
        help_text="Create custom-text to describe methodology and results of the "
        "assessment; insert tables, figures, and visualizations to using "
        '"smart-tags" which link to other data in HAWC.',
    )
    conflicts_of_interest = models.TextField(
        blank=True, help_text="Describe any conflicts of interest by the assessment-team.",
    )
    funding_source = models.TextField(
        blank=True, help_text="Describe the funding-source(s) for this assessment."
    )
    noel_name = models.PositiveSmallIntegerField(
        default=get_noel_name_default,
        choices=NOEL_NAME_CHOICES,
        verbose_name="NEL/NOEL/NOAEL name",
        help_text="What term should be used to refer to NEL/NOEL/NOAEL and LEL/LOEL/LOAEL?",
    )
    rob_name = models.PositiveSmallIntegerField(
        default=get_rob_name_default,
        choices=ROB_NAME_CHOICES,
        verbose_name="Risk of bias/Study evaluation name",
        help_text="What term should be used to refer to risk of bias/study evaluation questions?",
    )
    vocabulary = models.PositiveSmallIntegerField(
        choices=VocabularyNamespace.display_choices(),
        default=VocabularyNamespace.EHV.value,
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
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = "assessments"
    BREADCRUMB_PARENT = None

    def get_assessment(self):
        return self

    def get_absolute_url(self):
        return reverse("assessment:detail", args=(self.id,))

    def get_clear_cache_url(self):
        return reverse("assessment:clear_cache", args=(self.id,))

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
        return {
            "view": perms.can_view_object(user),
            "edit": perms.can_edit_object(user),
            "edit_assessment": perms.can_edit_assessment(user),
        }

    def user_can_view_object(self, user, perms: AssessmentPermissions = None) -> bool:
        if perms is None:
            perms = self.get_permissions()
        return perms.can_view_object(user)

    def user_can_edit_object(self, user, perms: AssessmentPermissions = None) -> bool:
        if perms is None:
            perms = self.get_permissions()
        return perms.can_edit_object(user)

    def user_can_edit_assessment(self, user, perms: AssessmentPermissions = None) -> bool:
        if perms is None:
            perms = self.get_permissions()
        return perms.can_edit_assessment(user)

    def user_is_part_of_team(self, user) -> bool:
        perms = self.get_permissions()
        return perms.part_of_team(user)

    def user_is_team_member_or_higher(self, user) -> bool:
        perms = self.get_permissions()
        return perms.team_member_or_higher(user)

    def get_vocabulary_display(self) -> str:
        # override default method
        if self.vocabulary:
            return VocabularyNamespace(self.vocabulary).display_name
        else:
            return ""

    def get_noel_names(self):
        if self.noel_name == NOEL_NAME_CHOICES_NEL:
            return NoelNames("NEL", "LEL", "No effect level", "Lowest effect level",)
        elif self.noel_name == NOEL_NAME_CHOICES_NOEL:
            return NoelNames(
                "NOEL", "LOEL", "No observed effect level", "Lowest observed effect level",
            )
        elif self.noel_name == NOEL_NAME_CHOICES_NOAEL:
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
            (apps.get_model("epimeta", "MetaProtocol"), dict(study__assessment_id=self.id),),
            (
                apps.get_model("epimeta", "MetaResult"),
                dict(protocol__study__assessment_id=self.id),
            ),
            (apps.get_model("invitro", "IVEndpoint"), dict(assessment_id=self.id)),
            (apps.get_model("mgmt", "Task"), dict(study__assessment_id=self.id)),
            (apps.get_model("riskofbias", "RiskOfBias"), dict(study__assessment_id=self.id),),
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

    @classmethod
    def size_df(cls) -> pd.DataFrame:
        qs = Assessment.objects.all().values("id", "name", "created", "last_updated")
        df1 = pd.DataFrame(qs).set_index("id")
        for annotation in [
            dict(num_references=models.Count("references")),
            dict(num_studies=models.Count("references__study")),
            dict(num_ani_endpoints=models.Count("baseendpoint__endpoint")),
            dict(num_epi_outcomes=models.Count("baseendpoint__outcome")),
            dict(num_epi_results=models.Count("baseendpoint__outcome__results")),
            dict(num_invitro_ivendpoints=models.Count("baseendpoint__ivendpoint")),
            dict(num_datapivots=models.Count("datapivot")),
            dict(num_viusals=models.Count("visuals")),
        ]:
            qs = Assessment.objects.all().values("id").annotate(**annotation)
            df2 = pd.DataFrame(qs).set_index("id")
            df1 = df1.merge(df2, left_index=True, right_index=True)
        return df1.reset_index().sort_values("id")

    def pms_and_team_users(self) -> models.QuerySet:
        # return users that are either project managers or team members
        return (
            HAWCUser.objects.filter(
                models.Q(assessment_pms=self.id) | models.Q(assessment_teams=self.id)
            )
            .order_by("id")
            .distinct("id")
        )


class Attachment(models.Model):
    objects = managers.AttachmentManager()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey("content_type", "object_id")
    title = models.CharField(max_length=128)
    attachment = models.FileField(upload_to="attachment")
    publicly_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    BREADCRUMB_PARENT = "content_object"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def get_edit_url(self):
        return reverse("assessment:attachment_update", args=[self.pk])

    def get_delete_url(self):
        return reverse("assessment:attachment_delete", args=[self.pk])

    def get_dict(self):
        return {
            "url": self.get_absolute_url(),
            "url_delete": self.get_delete_url(),
            "url_update": self.get_update_url(),
            "title": self.title,
            "description": self.description,
        }

    def get_assessment(self):
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
        max_length=30, help_text="Enter species in singular (ex: Mouse, not Mice)", unique=True,
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

    seconds = models.FloatField(validators=(MinValueValidator,))
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Time spent editing models"

    def __str__(self):
        return f"{self.content_type.model} {self.object_id}: {self.seconds}"

    @classmethod
    def get_cache_name(cls, url, session_key):
        return hash(f"{url}-{session_key}")

    @classmethod
    def set_start_time(cls, url, session_key):
        cache_name = cls.get_cache_name(url, session_key)
        now = timezone.now()
        # Set max time of one hour on a page; otherwise assume the page is
        # open but user is doing other things.
        cache.set(cache_name, now, 60 * 60 * 1)

    @classmethod
    def add_time_spent_job(cls, url, session_key, obj, assessment_id):
        cache_name = cls.get_cache_name(url, session_key)
        content_type_id = ContentType.objects.get_for_model(obj).id
        add_time_spent.delay(cache_name, obj.id, assessment_id, content_type_id)

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
        except models.ObjectDoesNotExist:
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
        column_names: List[str]

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
    def try_read_df(cls, data, suffix: str, worksheet_name: str = None) -> pd.DataFrame:
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
            func = read_excel
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
        JobType.TEST: jobs.test,
    }

    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(
        Assessment, blank=True, null=True, on_delete=models.CASCADE, related_name="jobs"
    )
    status = models.PositiveSmallIntegerField(
        choices=JobStatus.choices(), default=JobStatus.PENDING, editable=False
    )
    job = models.PositiveSmallIntegerField(choices=JobType.choices(), default=JobType.TEST)

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
        self.status = JobStatus.SUCCESS

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
        self.status = JobStatus.FAILURE

    def get_detail_url(self):
        return reverse("assessment:api:jobs-detail", args=(self.task_id,))


class Log(models.Model):
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
        if self.content_object is not None:
            return str(self.content_object) + " Log"
        if self.assessment is not None:
            return str(self.assessment) + " Log"
        return "Custom Log"

    def get_absolute_url(self):
        return reverse("assessment:log_detail", args=(self.id,))

    def get_api_url(self):
        # TODO delete api stuff?
        return reverse("assessment:api:logs-detail", args=(self.id,))

    def get_assessment(self):
        return self.assessment

    def user_can_view(self, user) -> bool:
        return (
            self.assessment.user_is_team_member_or_higher(user)
            if self.assessment
            else user.is_staff
        )


class Blog(models.Model):
    subject = models.CharField(max_length=128)
    content = models.TextField()
    rendered_content = models.TextField(editable=False)
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        return self.subject


class ContentTypeChoices(models.IntegerChoices):
    HOMEPAGE = 1
    ABOUT = 2
    RESOURCES = 3


class Content(models.Model):
    content_type = models.PositiveIntegerField(choices=ContentTypeChoices.choices, unique=True)
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
        cls, content_type: ContentTypeChoices, request: HttpRequest, context: Dict
    ) -> str:
        """Return rendered template response for the requested content.

        Return cached content for this page if one exists, or if it does not exist, render using
        the current context provided, cache, and return.
        """
        key = cls.get_cache_key(content_type)
        html = cache.get(key)
        if html is None:
            context = RequestContext(request, context)
            content = cls.objects.get(content_type=content_type)
            html = Template(content.template).render(context)
            cache.set(key, html, settings.CACHE_10_MIN)
        return html


reversion.register(DSSTox)
reversion.register(Assessment)
reversion.register(EffectTag)
reversion.register(Species)
reversion.register(Strain)
reversion.register(BaseEndpoint)
reversion.register(Dataset)
reversion.register(DatasetRevision)
reversion.register(Job)
reversion.register(Blog)
reversion.register(Content)
