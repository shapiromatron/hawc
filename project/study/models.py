import json
import logging
import os
import collections
import itertools

from django.db import models, transaction
from django.apps import apps
from django.core.exceptions import (ValidationError, ObjectDoesNotExist,
                                    MultipleObjectsReturned)
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse

from reversion import revisions as reversion

from assessment.models import Assessment
from assessment.serializers import AssessmentSerializer
from lit.models import Reference
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
        help_text="If True, this study, risk of bias, and extraction details "
                  "may be visible to reviewers and/or the general public "
                  "(if assessment-permissions allow this level of visibility). "
                  "Team-members and project-management can view both "
                  "published and unpublished studies.")
    summary = models.TextField(
        blank=True,
        verbose_name="Summary and/or extraction comments",
        help_text="Study summary or details on data-extraction needs.")

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

    def get_final_rob(self):
        try:
            return self.riskofbiases.get(final=True, active=True)
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise ValidationError(
                u'Multiple active final risk of bias reviews for "{}", '
                'there should only be one per study.'.format(self))

    def get_active_robs(self, with_final=True):
        if with_final:
            return self.riskofbiases\
               .filter(active=True)\
               .order_by('final', 'last_updated')\
               .prefetch_related('author')
        else:
            return self.riskofbiases\
               .filter(active=True, final=False)\
               .order_by('last_updated')\
               .prefetch_related('author')

    @property
    def qualities(self):
        return self.riskofbiases\
            .filter(final=True, active=True)\
            .first()\
            .scores.all()\
            .prefetch_related('metric', 'metric__domain')

    @classmethod
    def rob_scores(cls, assessment_id):
        return Study.objects\
            .filter(assessment_id=assessment_id)\
            .annotate(final_score=models.Sum(
                models.Case(
                    models.When(riskofbiases__active=True,
                                riskofbiases__final=True,
                                then='riskofbiases__scores__score'),
                    default=0)))\
            .values('id', 'short_citation', 'final_score')

    def optimized_for_serialization(self):
        return self.__class__.objects\
            .filter(id=self.id)\
            .prefetch_related(
                'identifiers',
                'searches',
                'riskofbiases__scores__metric__domain',
            ).first()


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

reversion.register(Study)
