from collections import OrderedDict
import json
import os

from django.db import models
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.http import urlquote
from django.shortcuts import HttpResponse

from reversion import revisions as reversion

from utils.models import get_crumbs
from utils.helper import HAWCDjangoJSONEncoder
from myuser.models import HAWCUser

from . import managers
from .tasks import add_time_spent


def get_cas_url(cas):
    if cas:
        return "{}?cas={}".format(reverse('assessment:cas_details'), urlquote(cas))
    else:
        return None


class Assessment(models.Model):
    objects = managers.AssessmentManager()

    name = models.CharField(
        max_length=80,
        verbose_name='Assessment Name',
        help_text="Describe the objective of the health-assessment.")
    year = models.PositiveSmallIntegerField(
        verbose_name='Assessment Year',
        help_text="Year with which the assessment should be associated.")
    version = models.CharField(
        max_length=80,
        verbose_name='Assessment Version',
        help_text="Version to describe the current assessment (i.e. draft, final, v1).")
    cas = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Chemical identifier (CAS)",
        help_text="Add a single CAS-number if one is available to describe the "
                  "assessment, otherwise leave-blank.")
    assessment_objective = models.TextField(
        blank=True,
        help_text="Describe the assessment objective(s), research questions, "
                  "or clarification on the purpose of the assessment.")
    project_manager = models.ManyToManyField(HAWCUser,
        related_name='assessment_pms',
        help_text="Has complete assessment control, including the ability to "
                  "add team members, make public, or delete an assessment. "
                  "You can add multiple project-managers.")
    team_members = models.ManyToManyField(HAWCUser,
        related_name='assessment_teams',
        blank=True,
        help_text="Can view and edit assessment components, "
                  "if project is editable. "
                  "You can add multiple team-members")
    reviewers = models.ManyToManyField(HAWCUser,
        related_name='assessment_reviewers',
        blank=True,
        help_text="Can view the assessment even if the assessment is not public, "
                  "but cannot add or change content. You can add multiple reviewers.")
    editable = models.BooleanField(
        default=True,
        help_text='Project-managers and team-members are allowed to edit assessment components.')
    public = models.BooleanField(
        default=False,
        help_text='The assessment can be viewed by the general public.')
    hide_from_public_page = models.BooleanField(
        default=False,
        help_text="If public, anyone with a link can view, "
                  "but do not show a link on the public-assessment page.")
    enable_literature_review = models.BooleanField(
        default=True,
        help_text="Search or import references from PubMed and other literature "
                  "databases, define inclusion, exclusion, or descriptive tags, "
                  "and apply these tags to retrieved literature for your analysis.")
    enable_project_management = models.BooleanField(
        default=True,
        help_text="Enable project management module for data extraction and "
                  "risk of bias. If enabled, each study will have multiple "
                  "tasks which can be assigned and tracked for completion.")
    enable_data_extraction = models.BooleanField(
        default=True,
        help_text="Extract animal bioassay, epidemiological, or in-vitro data from "
                  "key references and create customizable, dynamic visualizations "
                  "or summary data and associated metadata for display.")
    enable_risk_of_bias = models.BooleanField(
        default=True,
        help_text="Define criteria for a systematic review of literature, and apply "
                  "these criteria to references in your literature-review. "
                  "View details on findings and identify areas with a potential "
                  "risk of bias.")
    enable_bmd = models.BooleanField(
        default=True,
        verbose_name="Enable BMD modeling",
        help_text="Conduct benchmark dose (BMD) modeling on animal bioassay data "
                  "available in the HAWC database, using the US EPA's Benchmark "
                  "Dose Modeling Software (BMDS).")
    enable_summary_text = models.BooleanField(
        default=True,
        help_text="Create custom-text to describe methodology and results of the "
                  "assessment; insert tables, figures, and visualizations to using "
                  "\"smart-tags\" which link to other data in HAWC.")
    conflicts_of_interest = models.TextField(
        blank=True,
        help_text="Describe any conflicts of interest by the assessment-team.")
    funding_source = models.TextField(
        blank=True,
        help_text="Describe the funding-source(s) for this assessment.")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = 'assessments'

    def get_assessment(self):
        return self

    def get_absolute_url(self):
        return reverse('assessment:detail', args=[str(self.pk)])

    @property
    def cas_url(self):
        return get_cas_url(self.cas)

    class Meta:
        ordering = ("-created", )

    def __str__(self):
        return "%s (%s)" % (self.name, self.year)

    def user_permissions(self, user):
        return {
            'view': self.user_can_view_object(user),
            'edit': self.user_can_edit_object(user),
            'edit_assessment': self.user_can_edit_assessment(user)
        }

    def get_project_manager_emails(self):
        return self.project_manager.all().values_list('email', flat=True)

    def user_can_view_object(self, user):
        """
        Superusers can view all, noneditible reviews can be viewed, team
        members or project managers can view.
        Anonymous users on noneditable projects cannot view, nor can those who
        are non members of a project.
        """
        if self.public or user.is_superuser:
            return True
        elif user.is_anonymous():
            return False
        else:
            return ((user in self.project_manager.all()) or
                    (user in self.team_members.all()) or
                    (user in self.reviewers.all()))

    def user_can_edit_object(self, user):
        """
        If person has enhanced permissions beyond the general public, which may
        be used to view attachments associated with a study.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous():
            return False
        else:
            return (self.editable and
                    (user in self.project_manager.all() or
                     user in self.team_members.all()))

    def user_can_edit_assessment(self, user):
        """
        If person is superuser or assessment is editible and user is a project
        manager or team member.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous():
            return False
        else:
            return (user in self.project_manager.all())

    def user_is_part_of_team(self, user):
        """
        Used for permissions-checking if attachments for a study can be
        viewed. Checks to ensure user is part of the team.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous():
            return False
        else:
            return ((user in self.project_manager.all()) or
                    (user in self.team_members.all()) or
                    (user in self.reviewers.all()))

    def get_crumbs(self):
        return get_crumbs(self)


class Attachment(models.Model):
    objects = managers.AttachmentManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    title = models.CharField(max_length=128)
    attachment = models.FileField(upload_to="attachment")
    publicly_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

    def get_edit_url(self):
        return reverse('assessment:attachment_update', args=[self.pk])

    def get_delete_url(self):
        return reverse('assessment:attachment_delete', args=[self.pk])

    def get_dict(self):
        return {
            "url": self.get_absolute_url(),
            "url_delete": self.get_delete_url(),
            "url_update": self.get_update_url(),
            "title": self.title,
            "description": self.description
        }

    def get_assessment(self):
        return self.content_object.get_assessment()


class DoseUnits(models.Model):
    objects = managers.DoseUnitManager()

    name = models.CharField(
        max_length=20,
        unique=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "dose units"
        ordering = ("name", )

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
        unique=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "species"
        ordering = ("name", )

    def __str__(self):
        return self.name


class Strain(models.Model):
    objects = managers.StrainManager()

    species = models.ForeignKey(
        Species)
    name = models.CharField(
        max_length=30)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("species", "name"),)
        ordering = ("species", "name")

    def __str__(self):
        return self.name


class EffectTag(models.Model):
    objects = managers.EffectTagManager()

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True,
                            help_text="The URL (web address) used to describe this object (no spaces or special-characters).")

    class Meta:
        ordering = ("name", )

    def __str__(self):
        return self.name

    def get_json(self, json_encode=False):
        d = {}
        fields = ('pk', 'name')
        for field in fields:
            d[field] = getattr(self, field)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @staticmethod
    def get_name_list(queryset):
        return '|'.join(queryset.values_list("name", flat=True))


class BaseEndpoint(models.Model):
    """
    Parent quasi-abstract model for animal bioassay, epidemiology, or
    in-vitro endpoints used in assessment. Not fully abstract so efficient
    queries can pull data from all three more-specific endpoint types.
    """
    objects = managers.BaseEndpointManager()

    assessment = models.ForeignKey(Assessment, db_index=True)
    # Some denormalization but required for efficient capture of all endpoints
    # in assessment; major use case in HAWC.

    name = models.CharField(max_length=128, verbose_name="Endpoint name")
    effects = models.ManyToManyField(EffectTag, blank=True, verbose_name="Tags")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

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
        if hasattr(self, 'outcome'):
            d = self.outcome.get_json(*args, **kwargs)
        elif hasattr(self, 'endpoint'):
            d = self.endpoint.get_json(*args, **kwargs)
        elif hasattr(self, 'ivendpoint'):
            d = self.ivendpoint.get_json(*args, **kwargs)
        return d


class TimeSpentEditing(models.Model):
    objects = managers.TimeSpentEditingManager()

    seconds = models.FloatField(
        validators=(MinValueValidator, ))
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type', 'object_id')
    created = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Time spent editing models'

    def __str__(self):
        return f'{self.content_type.model} {self.object_id}: {self.seconds}'

    @classmethod
    def get_cache_name(cls, url, session_key):
        return hash(f'{url}-{session_key}')

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
        add_time_spent.delay(cache_name, obj.id,
                             assessment_id, content_type_id)

    @classmethod
    def add_time_spent(cls, cache_name, object_id, assessment_id, content_type_id):
        time_spent, created = cls.objects.get_or_create(
            content_type_id=content_type_id,
            object_id=object_id,
            assessment_id=assessment_id,
            defaults={'seconds': 0})

        now = timezone.now()
        start_time = cache.get(cache_name)
        if start_time:
            seconds_spent = now - start_time
            time_spent.seconds += seconds_spent.total_seconds()
            time_spent.save()
            cache.delete(cache_name)


reversion.register(Assessment)
reversion.register(EffectTag)
reversion.register(Species)
reversion.register(Strain)
reversion.register(BaseEndpoint)
