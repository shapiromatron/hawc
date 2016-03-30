import json
import logging
import os
import collections
import itertools

from django.db import models, transaction
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse

from reversion import revisions as reversion

from assessment.models import Assessment
from assessment.serializers import AssessmentSerializer
from lit.models import Reference
from myuser.models import HAWCUser
from utils.helper import HAWCDjangoJSONEncoder, SerializerHelper, cleanHTML
from utils.models import get_crumbs


class Study(Reference):

    STUDY_TYPE_CHOICES = (
        (0, 'Animal Bioassay'),
        (1, 'Epidemiology'),
        (4, 'Epidemiology meta-analysis/pooled analysis'),
        (2, 'In vitro'),
        (3, 'Other'))

    COI_REPORTED_CHOICES = (
        (0, 'Authors report they have no COI'),
        (1, 'Authors disclosed COI'),
        (2, 'Unknown'),
        (3, 'Not reported'))

    study_type = models.PositiveSmallIntegerField(
        choices=STUDY_TYPE_CHOICES,
        help_text="Type of data captured in the selected study. "
                  "This determines which fields are required for data-extraction.")
    short_citation = models.CharField(
        max_length=256,
        help_text="How the study should be identified (i.e. Smith et al. (2012), etc.)")
    full_citation = models.TextField(
        help_text="Complete study citation, in desired format.")
    coi_reported = models.PositiveSmallIntegerField(
        choices=COI_REPORTED_CHOICES,
        default=0,
        verbose_name="COI reported",
        help_text='Was a conflict of interest reported by the study authors?')
    coi_details = models.TextField(
        blank=True,
        verbose_name="COI details",
        help_text="Details related to potential or disclosed conflict(s) of interest")
    funding_source = models.TextField(blank=True)
    study_identifier = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Internal study identifier",
        help_text="Reference descriptor for assessment-tracking purposes "
                  "(for example, \"{Author, year, #EndNoteNumber}\")")
    contact_author = models.BooleanField(
        default=False,
        help_text="Was the author contacted for clarification of methods or results?")
    ask_author = models.TextField(
        blank=True,
        verbose_name="Correspondence details",
        help_text="Details on correspondence between data-extractor and author, if needed.")
    published = models.BooleanField(
        default=False,
        help_text="If True, this study, risk-of-bias, and extraction details "
                  "may be visible to reviewers and/or the general public "
                  "(if assessment-permissions allow this level of visibility). "
                  "Team-members and project-management can view both "
                  "published and unpublished studies.")
    summary = models.TextField(
        blank=True,
        verbose_name="Summary and/or extraction comments",
        help_text="Study summary or details on data-extraction needs.")
    qualities = fields.GenericRelation('StudyQuality', related_query_name='studies')

    COPY_NAME = "studies"

    class Meta:
        verbose_name_plural = "Studies"
        ordering = ("short_citation", )

    @classmethod
    def save_new_from_reference(cls, reference, attrs):
        """
        Save a new Study object from an existing reference object and the
        required information; difficult because of OneToOne relationship.

        Reference:
        https://github.com/lsaffre/lino/blob/master/lino/utils/mti.py
        """
        parent_link_field = Study._meta.parents.get(reference.__class__, None)
        attrs[parent_link_field.name]=reference
        for field in reference._meta.fields:
            attrs[field.name] = getattr(reference, field.name)
        return Study.objects.create(**attrs)

    @classmethod
    @transaction.atomic
    def copy_across_assessments(cls, studies, assessment):
        # copy selected studies from one assessment to another.
        cw = collections.defaultdict(dict)

        for study in studies:
            cw[Assessment.COPY_NAME][study.assessment_id] = assessment.id
            logging.info("Copying {} to  {}".format(study, assessment))

            # get child-types before changing
            type_ = study.study_type
            if type_ == 0:  # bioassay
                children = list(study.experiments.all())
            elif type_ == 1:  # epi
                children = list(study.study_populations.all())
            elif type_ == 2:  # in-vitro
                children = list(itertools.chain(
                    study.ivchemicals.all(),
                    study.ivcelltypes.all(),
                    study.ivexperiments.all()))
            elif type_ == 3:  # other
                children = []
            elif type_ == 4:  # meta-analysis
                children = list(study.meta_protocols.all())

            # copy reference and identifiers
            # (except RIS which is assessment-specific)
            ref = study.reference_ptr
            idents = ref.identifiers.filter(database__in=[0, 1, 2])\
                        .values_list('id', flat=True)
            ref.id = None
            ref.assessment = assessment
            ref.save()
            ref.identifiers.add(*idents)

            # copy study
            old_id = study.id
            study.id = None
            study.reference_ptr = ref
            study.assessment = assessment
            study.save()
            cw[cls.COPY_NAME][old_id] = study.id

            for child in children:
                child.copy_across_assessments(cw)

    def clean(self):
        pk_exclusion = {}
        if self.pk:
            pk_exclusion['pk'] = self.pk
        if Study.objects.filter(assessment=self.assessment,
                   short_citation=self.short_citation).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- short-citation name must be unique for assessment.')

    def __unicode__(self):
        return self.short_citation

    def get_absolute_url(self):
        return reverse('study:detail', args=[str(self.pk)])

    def get_assessment(self):
        return self.assessment

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def get_attachments_json(self):
        d = []
        for attachment in self.attachments.all():
            d.append(attachment.get_dict())
        return json.dumps(d, cls=HAWCDjangoJSONEncoder)

    def get_prior_versions_json(self):
        """
        Return a JSON list of other prior versions of selected model
        """
        versions = reversion.get_for_object(self)
        versions_json = []
        for version in versions:
            fields = version.field_dict
            fields['changed_by'] = version.revision.user.get_full_name()
            fields['updated'] = version.revision.date_created
            fields.pop('assessment')
            versions_json.append(fields)
        return json.dumps(versions_json, cls=DjangoJSONEncoder)

    def get_bioassay_endpoints(self):
        """
        Return a queryset of related bioassay endpoints for selected study
        """
        Endpoint = apps.get_model('animal', 'Endpoint')
        Experiment = apps.get_model('animal', 'Experiment')
        AnimalGroup = apps.get_model('animal', 'AnimalGroup')

        if self.study_type != 0:  # not a bioassay study
            return Endpoint.objects.none()

        return Endpoint.objects.filter(
                    animal_group__in=AnimalGroup.objects.filter(
                    experiment__in=Experiment.objects.filter(study=self)))

    @classmethod
    def flat_complete_header_row(cls):
        return (
            'study-id',
            'study-url',
            'study-short_citation',
            'study-full_citation',
            'study-coi_reported',
            'study-coi_details',
            'study-funding_source',
            'study-study_type',
            'study-study_identifier',
            'study-contact_author',
            'study-ask_author',
            'study-summary',
            'study-published'
        )

    @classmethod
    def flat_complete_data_row(cls, ser):
        return (
            ser['id'],
            ser['url'],
            ser['short_citation'],
            ser['full_citation'],
            ser['coi_reported'],
            ser['coi_details'],
            ser['funding_source'],
            ser['study_type'],
            ser['study_identifier'],
            ser['contact_author'],
            ser['ask_author'],
            cleanHTML(ser['summary']),
            ser['published']
        )

    @classmethod
    def get_docx_template_context(cls, assessment, queryset):
        studies = [SerializerHelper.get_serialized(study, json=False) for study in queryset]
        return {
            "assessment": AssessmentSerializer().to_representation(assessment),
            "studies": studies
        }

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @classmethod
    def get_choices(cls, assessment_id):
        return cls.objects\
                  .filter(assessment_id=assessment_id)\
                  .values_list('id', 'short_citation')

    def get_crumbs(self):
        return get_crumbs(self, parent=self.assessment)


class Attachment(models.Model):
    study = models.ForeignKey(Study, related_name="attachments")
    attachment = models.FileField(upload_to="study-attachment")

    def __unicode__(self):
        return self.filename

    def get_absolute_url(self):
        return reverse('study:attachment_detail', args=[self.pk])

    def get_delete_url(self):
        return reverse('study:attachment_delete', args=[self.pk])

    @property
    def filename(self):
        return os.path.basename(self.attachment.name)

    def get_dict(self):
        return {"url": self.get_absolute_url(),
                "filename": self.filename,
                "url_delete": self.get_delete_url()}

    def get_assessment(self):
        return self.study.assessment


class StudyQualityDomain(models.Model):
    assessment = models.ForeignKey('assessment.Assessment',
                                   related_name="sq_domains")
    name = models.CharField(max_length=128)
    description = models.TextField(default="")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assessment', 'name')
        ordering = ('pk', )

    def __unicode__(self):
        return self.name

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_default(cls, assessment):
        """
        Construct default risk of bias domains/metrics for an assessment.
        The risk-of-bias domains and metrics are those defined by NTP/OHAT
        protocols for risk-of-bias
        """
        fn = os.path.join(settings.PROJECT_PATH, 'study/fixtures/ohat_study_quality_defaults.json')
        with open(fn, 'r') as f:
            objects = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)

        for domain in objects["domains"]:
            d = StudyQualityDomain(assessment=assessment,
                                   name=domain["name"],
                                   description=domain["description"])
            d.save()
            StudyQualityMetric.build_metrics_for_one_domain(d, domain["metrics"])


class StudyQualityMetric(models.Model):
    domain = models.ForeignKey(StudyQualityDomain,
                               related_name="metrics")
    metric = models.CharField(max_length=256)
    description = models.TextField(blank=True,
                                   help_text='HTML text describing scoring of this field.')
    required_animal = models.BooleanField(
        default=True,
        verbose_name="Required for bioassay?",
        help_text="Is this metric required for animal bioassay studies?")
    required_epi = models.BooleanField(
        default=True,
        verbose_name="Required for epidemiology?",
        help_text="Is this metric required for human epidemiological studies?")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('domain', 'id')

    def __unicode__(self):
        return self.metric

    def get_assessment(self):
        return self.domain.get_assessment()

    @classmethod
    def get_required_metrics(self, assessment, study):
        filters = {
            "domain__in": StudyQualityDomain.objects.filter(assessment=assessment),
        }
        if study.study_type == 0:
            filters["required_animal"] = True
        elif study.study_type in [1,4]:
            filters["required_epi"] = True
        return StudyQualityMetric.objects.filter(**filters)

    @classmethod
    def build_metrics_for_one_domain(cls, domain, metrics):
        """
        Build multiple risk-of-bias metrics given a domain django object and a
        list of python dictionaries for each metric.
        """
        objs = []
        for metric in metrics:
            obj = StudyQualityMetric(**metric)
            obj.domain = domain
            objs.append(obj)
        StudyQualityMetric.objects.bulk_create(objs)


class StudyQuality(models.Model):

    STUDY_QUALITY_SCORE_CHOICES = (
        (1, 'Definitely high risk of bias'),
        (2, 'Probably high risk of bias'),
        (3, 'Probably low risk of bias'),
        (4, 'Definitely low risk of bias'),
        (0, 'Not applicable'))

    SCORE_SYMBOLS = {
        1: "--",
        2: "-",
        3: "+",
        4: "++",
        0: "-",
    }

    SCORE_SHADES = {
        1: "#CC3333",
        2: "#FFCC00",
        3: "#6FFF00",
        4: "#00CC00",
        0: "#FFCC00",
    }

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    metric = models.ForeignKey(StudyQualityMetric, related_name='qualities')
    score = models.PositiveSmallIntegerField(choices=STUDY_QUALITY_SCORE_CHOICES, default=4)
    notes = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(HAWCUser,
        related_name='qualities',
        blank=True,
        null=True)

    class Meta:
        ordering = ("content_type", "object_id", "metric")
        verbose_name_plural = "Study Qualities"
        unique_together = (("content_type", "object_id", "metric"), )

    def __unicode__(self):
        return '{}: {}'.format(self.metric, self.score)

    def get_assessment(self):
        return self.content_object.get_assessment()

    def get_absolute_url(self):
        if type(self.content_object) is Study:
            return reverse('study:sqs_detail', args=[str(self.study.pk)])
        else:
            return self.content_object.get_absolute_url()

    def get_edit_url(self):
        return reverse('study:sq_update', args=[self.pk])

    def get_delete_url(self):
        return reverse('study:sq_delete', args=[self.pk])

    @property
    def score_symbol(self):
        return self.SCORE_SYMBOLS[self.score]

    @property
    def score_shade(self):
        return self.SCORE_SHADES[self.score]

    @staticmethod
    def flat_complete_header_row():
        return (
            'sq-domain_id',
            'sq-domain_name',
            'sq-domain_description',
            'sq-metric_id',
            'sq-metric_metric',
            'sq-metric_description',
            'sq-id',
            'sq-notes',
            'sq-score_description',
            'sq-score'
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['metric']['domain']['id'],
            ser['metric']['domain']['name'],
            ser['metric']['domain']['description'],
            ser['metric']['id'],
            ser['metric']['metric'],
            ser['metric']['description'],
            ser['id'],
            cleanHTML(ser['notes']),
            ser['score_description'],
            ser['score']
        )


reversion.register(Study)
reversion.register(StudyQualityDomain)
reversion.register(StudyQualityMetric)
reversion.register(StudyQuality)
