from collections import OrderedDict
import logging
import json
import os

from django.db import models
from django.db.models.loading import get_model
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from mailmerge import MailMerge
import reversion

from utils.helper import HAWCDjangoJSONEncoder
from myuser.models import HAWCUser

from .tasks import get_chemspider_details


class Assessment(models.Model):
    name = models.CharField(max_length=80, verbose_name='Assessment Name')
    cas = models.CharField(max_length=40, blank=True,
                           verbose_name="Chemical identifier (CAS)",
                           help_text="Add a CAS number if assessment is for one chemical, otherwise leave-blank.")
    year = models.PositiveSmallIntegerField(verbose_name='Assessment Year')  # not required - delete?
    version = models.CharField(max_length=80, verbose_name='Assessment Version')  # http://stackoverflow.com/questions/522997/ todo: make autoincrement
    project_manager = models.ManyToManyField(HAWCUser, related_name='assessment_pms', null=False,  # todo: move all these into one m2m table w/ metadata
        help_text="Have full assessment control, including the ability to add team members, make public, or delete an assessment.")
    team_members = models.ManyToManyField(HAWCUser, related_name='assessment_teams', null=True, blank=True,
        help_text="Can view and edit assessment components, when the project is editable.")
    reviewers = models.ManyToManyField(HAWCUser, related_name='assessment_reviewers', null=True, blank=True,
        help_text="Can view assessment components in read-only mode; can also add comments.")
    editable = models.BooleanField(default=True,
        help_text='Team-members are allowed to edit assessment components.')
    public = models.BooleanField(default=False,
        help_text='The assessment and all components are publicly assessable.')
    enable_literature_review = models.BooleanField(default=True,
        help_text="Search or import references from PubMed and other literature "
                  "databases, define inclusion, exclusion, or descriptive tags, "
                  "and apply these tags to retrieved literature for your analysis.")
    enable_data_extraction = models.BooleanField(default=True,
        help_text="Extract animal bioassay, epidemiological, or in-vitro data from "
                  "key references and create customizable, dynamic visualizations "
                  "or summary data and associated metadata for display.")
    enable_study_quality = models.BooleanField(default=True,
        help_text="Define criteria for a systematic review of literature, and apply "
                  "these criteria to references in your literature-review. "
                  "View details on findings and identify areas with a potential "
                  "risk-of-bias.")
    enable_bmd = models.BooleanField(default=True,
        verbose_name="Enable BMD modeling",
        help_text="Conduct benchmark dose (BMD) modeling on animal bioassay data "
                  "available in the HAWC database, using the US EPA's Benchmark "
                  "Dose Modeling Software (BMDS).")
    enable_reference_values = models.BooleanField(default=True,
        help_text="Define a point-of-departure, apply uncertainty factors, and "
                  "derive reference values by route of exposure.")
    enable_summary_text = models.BooleanField(default=True,
        help_text="Create custom-text to describe methodology and results of the "
                  "assessment; insert tables, figures, and visualizations to using "
                  "\"smart-tags\" which link to other data in HAWC.")
    enable_comments = models.BooleanField(default=True,
        help_text="Enable comments from reviewers or the general-public on "
                  "datasets or findings; comment-functionality and visibility "
                  "can be controlled in advanced-settings.")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

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

    class Meta:
        ordering = ("-created", )

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.year)

    def get_project_manager_emails(self):
        return self.project_manager.all().values_list('email', flat=True)

    def user_can_view_object(self, user):
        """
        Superusers can view all, noneditible reviews can be viewed, team members or
        project managers can view.
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
            return ((user in self.project_manager.all()) or
                    (user in self.team_members.all()))

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
        viewed. Checks to ensure user is authenticated and at least a team-member.
        """
        if user.is_superuser:
            return True
        elif user.is_anonymous():
            return False
        else:
            return ((user in self.project_manager.all()) or
                    (user in self.team_members.all()) or
                    (user in self.reviewers.all()))

    def get_CAS_details(self):
        task = get_chemspider_details.delay(self.cas)
        v = task.get(timeout=60)
        if v:
            return v

    @classmethod
    def get_viewable_assessments(cls, user, exclusion_id=None):
        """
        Return queryset of all assessments which that user is able to view,
        optionally excluding assessment exclusion_id,
        not including public assessments
        """
        return Assessment.objects\
            .filter(Q(project_manager=user) | Q(team_members=user) | Q(reviewers=user))\
            .exclude(id=exclusion_id)\
            .distinct()


@receiver(post_save, sender=Assessment)
def default_configuration(sender, instance, created, **kwargs):
    """
    Created default assessment settings when a new assessment instance
    is created.
    """
    if created:

        logging.info("Creating default literature inclusion/exclusion tags")
        get_model('lit', 'ReferenceFilterTag').build_default(instance)
        get_model('lit', 'Search').build_default(instance)

        logging.info("Creating default settings for study-quality criteria")
        get_model('study', 'StudyQualityDomain').build_default(instance)

        logging.info("Creating new BMD settings assessment creation")
        get_model('bmd', 'LogicField').build_defaults(instance)
        get_model('bmd', 'BMD_Assessment_Settings')(assessment=instance).save()

        logging.info("Creating default summary text")
        get_model('summary', 'SummaryText').build_default(instance)

        logging.info("Building default comment settings")
        get_model('comments', 'CommentSettings')(assessment=instance).save()

        logging.info("Building in-vitro endpoint category-root")
        get_model('invitro', 'IVEndpointCategory').create_root(assessment_id=instance.pk)


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


class BaseEndpoint(models.Model):
    """
    Parent quasi-abstract model for animal bioassay, epidemiology, or
    in-vitro endpoints used in assessment. Not fully abstract so efficient
    queries can pull data from all three more-specific endpoint types.
    """
    assessment = models.ForeignKey(Assessment)
    # Some denormalization but required for efficient capture of all endpoints
    # in assessment; major use case in HAWC.

    name = models.CharField(max_length=128, verbose_name="Endpoint name")
    effects = models.ManyToManyField(EffectTag, blank=True, null=True,
                                     verbose_name="Tags")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def get_assessment(self):
        return self.assessment

    @staticmethod
    def clear_cache():
        pks = BaseEndpoint.objects.all().values_list('pk', flat=True)
        BaseEndpoint.d_response_delete_cache(pks)

    @classmethod
    def d_response_delete_cache(cls, endpoint_pks):
        keys = ['endpoint-json-{pk}'.format(pk=pk) for pk in endpoint_pks]
        logging.info('removing cache: {caches}'.format(caches=', '.join(keys)))
        cache.delete_many(keys)

    def getDict(self):
        """
        Return flat-dictionary of BaseEndpoint.
        """
        tagnames = EffectTag.get_name_list(self.effects)
        return OrderedDict((("endpoint-name", self.name),
                            ("endpoint-effects", tagnames)))

    def get_json(self, *args, **kwargs):
        """
        Use the appropriate child-class to generate JSON response object, or
        return an empty object.
        """
        d = {}
        if hasattr(self, 'assessedoutcome'):
            d = self.assessedoutcome.get_json(*args, **kwargs)
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

    def get_mailmerge(self):
        return MailMerge(self.get_full_path())

    @classmethod
    def get_by_report_type(cls, queryset):
        templates = OrderedDict()
        for typ in cls.REPORT_TYPE_CHOICES:
            templates[typ[0]]=[]

        for obj in queryset:
            templates[obj.report_type].append(obj)

        return templates

    @classmethod
    def get_template(cls, template_id, assessment_id, report_type):
        # Return a template object if one exists which matches the specified
        # criteria, else throw an ObjectDoesNotExist error
        qs = cls.objects\
                .filter(id=template_id, report_type=2)\
                .filter(Q(assessment=assessment_id) | Q(assessment=None))

        if qs.count() == 1:
            return qs[0]
        else:
            raise models.ObjectDoesNotExist()


reversion.register(Assessment)
reversion.register(EffectTag)
reversion.register(BaseEndpoint)
reversion.register(ChangeLog)
reversion.register(ReportTemplate)
