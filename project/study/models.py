import json
import logging
import os
from collections import OrderedDict

from django.db import models
from django.db.models.loading import get_model
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

import reversion

from utils.helper import HAWCDjangoJSONEncoder, build_excel_file, excel_export_detail
from lit.models import Reference


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
        choices=STUDY_TYPE_CHOICES)
    short_citation = models.CharField(
        max_length=256,
        blank=False) # initial guess provided from reference; can be edited
    full_citation = models.TextField(
        blank=False) # initial guess provided from reference; can be edited
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
                  "(for example, \"{Author, year, #EndnoteNumber}\")")
    contact_author = models.BooleanField(
        default=False,
        help_text="Does author need to be contacted?")
    ask_author = models.TextField(
        blank=True,
        help_text="Details on author correspondence")
    published = models.BooleanField(
        default=False,
        help_text="If True, reviewers and the public can see study "
                  "(if assessment-permissions allow this level of visibility). "
                  "Team-members can always see studies, even if they are "
                  "not-yet published.")
    summary = models.TextField(
        blank=True,
        help_text="Study summary as written by team-members, or details on "
                  "data-extraction requirements by project-management")

    class Meta:
        verbose_name_plural = "Studies"
        ordering = ("short_citation", )

    def save(self, *args, **kwargs):
        Endpoint = get_model('animal', 'Endpoint')
        AssessedOutcome = get_model('epi', 'AssessedOutcome')
        super(Study, self).save(*args, **kwargs)

        #clear animal endpoints cache
        endpoint_pks = list(Endpoint.objects.all()
                            .filter(animal_group__experiment__study=self.pk)
                            .values_list('pk', flat=True))
        Endpoint.d_response_delete_cache(endpoint_pks)

        # clear assessed outcome endpoints cache
        ao_pks = list(AssessedOutcome.objects.all()
                      .filter(exposure__study_population__study=self.pk)
                      .values_list('pk', flat=True))
        AssessedOutcome.d_response_delete_cache(ao_pks)
        logging.debug("Resetting cache for assessed outcome from study change")

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
        s=Study(**attrs)
        s.save()
        return s

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
        """
        Returns a JSON representation of itself and all study-quality
        information.
        """
        d = {"study_url": self.get_absolute_url()}
        fields = ('pk', 'full_citation', 'short_citation',
                  'coi_details', 'funding_source',
                  'study_identifier', 'contact_author', 'ask_author',
                  'summary')
        for field in fields:
            d[field] = getattr(self, field)

        d['study_type'] = self.get_study_type_display()
        d['study_quality'] = []
        d['coi_reported'] = self.get_coi_reported_display()
        for sq in self.qualities.all().select_related('metric'):
            d['study_quality'].append(sq.get_json(json_encode=False))

        d['reference'] = self.reference_ptr.get_json(json_encode=False)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

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

    def docx_print(self, report, heading_level):
        """
        Word report format for printing a study.
        """

        # define content
        title = u'Study summary: {0}'.format(self.short_citation)
        paras = (
            u'Full Citation: {0}'.format(self.full_citation),
            u'Text summary: {0}'.format(strip_tags(self.summary)),
            )

        # print to document
        report.doc.add_heading(title, level=heading_level)
        for para in paras:
            report.doc.add_paragraph(para)
        report.doc.add_page_break()

        for endpoint in self.get_bioassay_endpoints():
            endpoint.docx_print(report, heading_level+1)

    def get_bioassay_endpoints(self):
        """
        Return a queryset of related bioassay endpoints for selected study
        """
        Endpoint = get_model('animal', 'Endpoint')
        Experiment = get_model('animal', 'Experiment')
        AnimalGroup = get_model('animal', 'AnimalGroup')

        if  self.study_type != 0: # not a bioassay study
            return Endpoint.objects.none()

        return Endpoint.objects.filter(
                    animal_group__in=AnimalGroup.objects.filter(
                    experiment__in=Experiment.objects.filter(study=self)))

    def getDict(self):
        """
        Return flat-dictionary of Study.
        """
        return OrderedDict((("study-pk", self.pk),
                            ("study-url", self.get_absolute_url()),
                            ("study-short_citation", self.short_citation),
                            ("study-full_citation", self.full_citation),
                            ("study-coi_reported", self.get_coi_reported_display()),
                            ("study-coi_details", self.coi_details),
                            ("study-funding_source", self.funding_source),
                            ("study-study_type", self.get_study_type_display()),
                            ("study-study_identifier", self.study_identifier),
                            ("study-contact_author", self.contact_author),
                            ("study-ask_author", self.ask_author),
                            ("study-summary", self.summary)))

    @staticmethod
    def excel_export_detail(dic, isHeader):
        return excel_export_detail(dic, isHeader)

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
        return ('study-pk',
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
                'study-summary')


    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (dic['pk'],
                dic['study_url'],
                dic['short_citation'],
                dic['full_citation'],
                dic['coi_reported'],
                dic['coi_details'],
                dic['funding_source'],
                dic['study_type'],
                dic['study_identifier'],
                dic['contact_author'],
                dic['ask_author'],
                dic['summary'])

    @staticmethod
    def study_bias_excel_export(queryset):
        # full export of study bias, designed for import/export of
        # data using a flat-xls file.
        sheet_name = 'study-bias'
        headers = Study.excel_export_header()
        data_rows_func = Study.build_export_rows
        return build_excel_file(sheet_name, headers, queryset, data_rows_func)

    @staticmethod
    def excel_export_header():
        # build export header column names for full export
        lst = []
        lst.extend(Study.build_export_from_json_header())
        lst.extend(StudyQuality.build_export_from_json_header())
        return lst

    @staticmethod
    def build_export_rows(ws, queryset, *args, **kwargs):
        # build export data rows for full-export
        def try_float(str):
            try:
                return float(str)
            except:
                return str

        i = 0
        for study in queryset:
            d = study.get_json(json_encode=False)
            fields = []
            fields.extend(Study.build_flat_from_json_dict(d))
            # build a row for each aog
            for sq in d['study_quality']:
                i+=1
                new_fields = list(fields)  # clone
                new_fields.extend(StudyQuality.build_flat_from_json_dict(sq))
                for j, val in enumerate(new_fields):
                    ws.write(i, j, try_float(val))


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
    changed = models.DateTimeField(auto_now=True)

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
        Construct default study quality domains/metrics for an assessment.
        The study-quality domains and metrics are those defined by NTP/OHAT
        protocols for study-bias
        """
        fn = os.path.join(settings.PROJECT_PATH, 'study/fixtures/ohat_study_quality_defaults.json')
        with open(fn, 'r') as f:
            objects = json.loads(f.read())

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
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('domain', 'metric')

    def __unicode__(self):
        return self.metric

    def get_assessment(self):
        return self.domain.get_assessment()

    def get_json(self, json_encode=True):
        """
        Returns a JSON representation of itself and all study-quality
        information.
        """
        d = {}
        fields = ('id', 'metric', 'description', 'created', 'changed')
        for field in fields:
            d[field] = getattr(self, field)
        d['domain'] = self.domain.pk
        d['domain_text'] = self.domain.__unicode__()

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @classmethod
    def get_metrics_for_assessment(self, assessment):
        return StudyQualityMetric.objects.filter(
                domain__in=StudyQualityDomain.objects.filter(
                    assessment=assessment))

    @classmethod
    def build_metrics_for_one_domain(cls, domain, metrics):
        """
        Build multiple study-quality metrics given a domain django object and a
        list of python dictionaries for each metric.
        """
        objects = []
        for metric in metrics:
            objects.append(StudyQualityMetric(domain=domain,
                                              metric=metric["metric"],
                                              description=metric["description"]))
        StudyQualityMetric.objects.bulk_create(objects)


class StudyQuality(models.Model):

    STUDY_QUALITY_SCORE_CHOICES = (
        (1, 'Definitely high risk of bias'),
        (2, 'Probably high risk of bias'),
        (3, 'Probably low risk of bias'),
        (4, 'Definitely low risk of bias'),
        (0, 'Not applicable'))

    study = models.ForeignKey(Study, related_name='qualities')
    metric = models.ForeignKey(StudyQualityMetric, related_name='qualities')
    score = models.PositiveSmallIntegerField(choices=STUDY_QUALITY_SCORE_CHOICES, default=4)
    notes = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('study', 'metric')
        verbose_name_plural = "Study Qualities"
        unique_together = (("study", "metric"),)

    def __unicode__(self):
        return '{study}: {metric}'.format(study=self.study, metric=self.metric)

    def get_absolute_url(self):
        return reverse('study:sq_detail', args=[str(self.study.pk)])

    def get_json(self, json_encode=True):
        """
        Returns a JSON representation of itself and all study-quality
        information.
        """
        d = {'score_description': self.get_score_display()}
        fields = ('pk', 'score', 'notes')
        for field in fields:
            d[field] = getattr(self, field)
        d['metric'] = self.metric.get_json(json_encode=False)
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    def save(self, *args, **kwargs):
        super(StudyQuality, self).save(*args, **kwargs)
        Endpoint = get_model('animal', 'Endpoint')
        endpoint_pks = list(Endpoint.objects.all()
                            .filter(animal_group__experiment__study__qualities=self.pk)
                            .values_list('pk', flat=True))
        Endpoint.d_response_delete_cache(endpoint_pks)

    @staticmethod
    def build_export_from_json_header():
        # used for full-export/import functionalities
        return ('sq-domain-pk',
                'sq-domain_text',
                'sq-metric-pk',
                'sq-metric-metric',
                'sq-metric-description',
                'sq-pk',
                'sq-notes',
                'sq-score_description',
                'sq-score')

    @staticmethod
    def build_flat_from_json_dict(dic):
        # used for full-export/import functionalities
        return (dic['metric']['domain'],
                dic['metric']['domain_text'],
                dic['metric']['id'],
                dic['metric']['metric'],
                dic['metric']['description'],
                dic['pk'],
                dic['notes'],
                dic['score_description'],
                dic['score'])


reversion.register(Study)
reversion.register(StudyQualityDomain)
reversion.register(StudyQualityMetric)
reversion.register(StudyQuality)
