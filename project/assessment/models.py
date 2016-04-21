from collections import OrderedDict
import json
import os
from StringIO import StringIO

from django.db import models
from django.apps import apps
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.http import urlquote
from django.shortcuts import HttpResponse

from mailmerge import MailMerge
from reversion import revisions as reversion

from utils.models import get_crumbs
from utils.helper import HAWCDjangoJSONEncoder
from myuser.models import HAWCUser


def get_cas_url(cas):
    if cas:
        return u"{}?cas={}".format(reverse('assessment:cas_details'), urlquote(cas))
    else:
        return None


class Assessment(models.Model):
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
                  "but cannot add or change content. Reviewers may optionally add "
                  "comments, if this feature is enabled. You can add multiple reviewers.")
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
    enable_data_extraction = models.BooleanField(
        default=True,
        help_text="Extract animal bioassay, epidemiological, or in-vitro data from "
                  "key references and create customizable, dynamic visualizations "
                  "or summary data and associated metadata for display.")
    enable_study_quality = models.BooleanField(
        default=True,
        help_text="Define criteria for a systematic review of literature, and apply "
                  "these criteria to references in your literature-review. "
                  "View details on findings and identify areas with a potential "
                  "risk-of-bias.")
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
    enable_comments = models.BooleanField(
        default=True,
        help_text="Enable comments from reviewers or the general-public on "
                  "datasets or findings; comment-functionality and visibility "
                  "can be controlled in advanced-settings.")
    conflicts_of_interest = models.TextField(
        blank=True,
        help_text="Describe any conflicts of interest by the assessment-team.")
    funding_source = models.TextField(
        blank=True,
        help_text="Describe the funding-source(s) for this assessment.")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    rob_reviewers = fields.GenericRelation('riskofbias.RiskOfBiasReviewers', related_query_name='assessment')

    COPY_NAME = 'assessments'

    def get_prior_versions_json(self):
        """
        Return a JSON list of other prior versions of selected model
        """
        def get_users(pk_list):
            users = []
            for pk in pk_list:
                try:
                    u = HAWCUser.objects.get(pk=pk)
                except:
                    deleted_users = reversion.get_deleted(HAWCUser)
                    u = deleted_users.get(pk=pk)
                users.append(u.get_full_name())
            return '<br>'.join(sorted(users))

        versions = reversion.get_for_object(self)
        versions_json = []
        for version in versions:
            fields = version.field_dict
            # replace M2M with objects in field-list
            fields['project_manager'] = get_users(fields['project_manager'])
            fields['team_members'] = get_users(fields['team_members'])
            fields['reviewers'] = get_users(fields['reviewers'])
            fields['changed_by'] = version.revision.user.get_full_name()
            fields['updated'] = version.revision.date_created
            versions_json.append(fields)
        return json.dumps(versions_json, cls=DjangoJSONEncoder)

    def get_assessment(self):
        return self

    def get_absolute_url(self):
        return reverse('assessment:detail', args=[str(self.pk)])

    @property
    def cas_url(self):
        return get_cas_url(self.cas)

    class Meta:
        ordering = ("-created", )

    def __unicode__(self):
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

    def user_can_view_attachments(self, user):
        """
        Used for permissions-checking if attachments for a study can be
        viewed. Checks to ensure user is authenticated and >= team-member.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous():
            return False
        else:
            return ((user in self.project_manager.all()) or
                    (user in self.team_members.all()) or
                    (user in self.reviewers.all()))

    @classmethod
    def get_viewable_assessments(cls, user, exclusion_id=None, public=False):
        """
        Return queryset of all assessments which that user is able to view,
        optionally excluding assessment exclusion_id,
        not including public assessments
        """
        filters = (Q(project_manager=user) | Q(team_members=user) | Q(reviewers=user))
        if public:
            filters |= (Q(public=True) & Q(hide_from_public_page=False))
        return Assessment.objects\
            .filter(filters)\
            .exclude(id=exclusion_id)\
            .distinct()

    @classmethod
    def get_editable_assessments(cls, user, exclusion_id=None):
        """
        Return queryset of all assessments which that user is able to edit,
        optionally excluding assessment exclusion_id,
        not including public assessments
        """
        return Assessment.objects\
            .filter(Q(project_manager=user) | Q(team_members=user))\
            .exclude(id=exclusion_id)\
            .distinct()

    def get_crumbs(self):
        return get_crumbs(self)


class Attachment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    title = models.CharField(max_length=128)
    attachment = models.FileField(upload_to="attachment")
    publicly_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
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

    @classmethod
    def get_attachments(cls, obj, isPublic):
        filters = {
            "content_type": ContentType.objects.get_for_model(obj),
            "object_id": obj.id
        }
        if isPublic:
            filters["publicly_available"] = True
        return cls.objects.filter(**filters)


class DoseUnits(models.Model):
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

    def __unicode__(self):
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

    @classmethod
    def json_all(cls):
        return json.dumps(list(cls.objects.all().values()), cls=HAWCDjangoJSONEncoder)

    @classmethod
    def get_animal_units(cls, assessment):
        """
        Returns a list of the dose-units which are used in the selected
        assessment for animal bioassay data.
        """
        Study = apps.get_model('study', 'Study')
        Experiment = apps.get_model('animal', 'Experiment')
        AnimalGroup = apps.get_model('animal', 'AnimalGroup')
        DosingRegime = apps.get_model('animal', 'DosingRegime')
        DoseGroup = apps.get_model('animal', 'DoseGroup')
        return cls.objects.filter(
            dosegroup__in=DoseGroup.objects.filter(
                dose_regime__in=DosingRegime.objects.filter(
                    dosed_animals__in=AnimalGroup.objects.filter(
                        experiment__in=Experiment.objects.filter(
                            study__in=Study.objects.filter(
                                assessment=assessment))))))\
            .values_list('name', flat=True)\
            .distinct()


class Species(models.Model):
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

    def __unicode__(self):
        return self.name


class Strain(models.Model):
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

    def __unicode__(self):
        return self.name


class EffectTag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True,
                            help_text="The URL (web address) used to describe this object (no spaces or special-characters).")

    class Meta:
        ordering = ("name", )

    def __unicode__(self):
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

    @classmethod
    def get_name_list(self, queryset):
        return '|'.join(queryset.values_list("name", flat=True))

    @classmethod
    def get_choices(cls, assessment_id):
        return cls.objects\
                .filter(baseendpoint__assessment_id=assessment_id)\
                .values_list('id', 'name')\
                .distinct()\
                .order_by('name')


class BaseEndpoint(models.Model):
    """
    Parent quasi-abstract model for animal bioassay, epidemiology, or
    in-vitro endpoints used in assessment. Not fully abstract so efficient
    queries can pull data from all three more-specific endpoint types.
    """
    assessment = models.ForeignKey(Assessment, db_index=True)
    # Some denormalization but required for efficient capture of all endpoints
    # in assessment; major use case in HAWC.

    name = models.CharField(max_length=128, verbose_name="Endpoint name")
    effects = models.ManyToManyField(EffectTag, blank=True, verbose_name="Tags")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
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
            d = self.endpoint.d_response(*args, **kwargs)
        elif hasattr(self, 'ivendpoint'):
            d = self.ivendpoint.get_json(*args, **kwargs)
        return d


class ChangeLog(models.Model):
    date = models.DateField(
        unique=True)
    name = models.CharField(
        unique=True,
        verbose_name="Release name",
        help_text="Adjective + noun combination",
        max_length=128)
    slug = models.SlugField(
        verbose_name="URL slug",
        max_length=128)
    header = models.TextField(
        help_text="One-paragraph description of major changes made")
    detailed_list = models.TextField(
        help_text="Detailed bulleted-list of individual item-changes")

    class Meta:
        ordering = ("-date", )

    def __unicode__(self):
        return "{0}: {1}".format(self.date, self.name)

    def get_absolute_url(self):
        return reverse('change_log_detail', kwargs={'slug': self.slug})


class ReportTemplate(models.Model):

    REPORT_TYPE_CHOICES = (
        (0, 'Literature search'),
        (1, 'Studies and study-quality'),
        (2, 'Animal bioassay'),
        (3, 'Epidemiology'),
        (4, 'Epidemiology meta-analysis/pooled analysis'),
        (5, 'In vitro'))

    assessment = models.ForeignKey(
        'assessment.assessment',
        related_name="templates",
        blank=True,
        null=True)
    description = models.CharField(
        max_length=256)
    report_type = models.PositiveSmallIntegerField(
        choices=REPORT_TYPE_CHOICES)
    template = models.FileField(
        upload_to="templates")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    def __unicode__(self):
        return self.description

    def get_absolute_url(self):
        # show list view; no detail-view
        return reverse("assessment:template_detail", kwargs={"pk": self.pk})

    def get_assessment(self):
        return self.assessment

    def get_full_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.template.name)

    def get_filename(self):
        return os.path.basename(self.template.name)

    def apply_mailmerge(self, context, filename="example.docx"):
        # Return a django request response with a docx download.
        docx = StringIO()

        mailmerge = MailMerge(self.get_full_path())
        mailmerge.merge(context)
        mailmerge.write(docx)
        mailmerge.close()

        # return response
        docx.seek(0)
        response = HttpResponse(docx)
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return response

    @classmethod
    def get_by_report_type(cls, queryset):
        templates = OrderedDict()
        for typ in cls.REPORT_TYPE_CHOICES:
            templates[typ[0]] = []

        for obj in queryset:
            templates[obj.report_type].append(obj)

        return templates

    @classmethod
    def get_template(cls, template_id, assessment_id, report_type):
        # Return a template object if one exists which matches the specified
        # criteria, else throw an ObjectDoesNotExist error
        qs = cls.objects\
                .filter(id=template_id, report_type=report_type)\
                .filter(Q(assessment=assessment_id) | Q(assessment=None))

        if qs.count() == 1:
            return qs[0]
        else:
            raise models.ObjectDoesNotExist()


reversion.register(Assessment)
reversion.register(EffectTag)
reversion.register(Species)
reversion.register(Strain)
reversion.register(BaseEndpoint)
reversion.register(ChangeLog)
reversion.register(ReportTemplate)
