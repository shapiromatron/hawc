import collections
import itertools
import logging
import os

from django.apps import apps
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, ValidationError
from django.db import models, transaction
from django.http import Http404
from django.urls import reverse
from reversion import revisions as reversion

from ..assessment.models import Assessment
from ..assessment.serializers import AssessmentSerializer
from ..common.forms import ASSESSMENT_UNIQUE_MESSAGE
from ..common.helper import SerializerHelper, cleanHTML
from ..lit.models import Reference, Search
from . import managers

logger = logging.getLogger(__name__)


class Study(Reference):
    objects = managers.StudyManager()

    COI_REPORTED_CHOICES = (
        (4, "---"),
        (0, "Authors report they have no COI"),
        (1, "Authors disclosed COI"),
        (5, "Not reported; no COI is inferred based on author affiliation and/or funding source",),
        (6, "Not reported; a COI is inferred based on author affiliation and/or funding source",),
        (3, "Not reported"),
        (2, "Unknown"),
    )

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
    }

    bioassay = models.BooleanField(
        verbose_name="Animal bioassay",
        default=False,
        help_text="Study contains animal bioassay data",
    )
    epi = models.BooleanField(
        verbose_name="Epidemiology", default=False, help_text="Study contains epidemiology data",
    )
    epi_meta = models.BooleanField(
        verbose_name="Epidemiology meta-analysis",
        default=False,
        help_text="Study contains epidemiology meta-analysis/pooled analysis data",
    )
    in_vitro = models.BooleanField(default=False, help_text="Study contains in-vitro data")
    short_citation = models.CharField(
        max_length=256,
        help_text="How the study should be identified (i.e. Smith et al. (2012), etc.)",
    )
    full_citation = models.TextField(help_text="Complete study citation, in desired format.")
    coi_reported = models.PositiveSmallIntegerField(
        choices=COI_REPORTED_CHOICES,
        default=4,
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
        help_text="This field is often left blank, but used to add comments on data extraction, "
        "e.g., reference to full study reports or indicating which outcomes/endpoints "
        "in a study were not extracted.",
    )
    editable = models.BooleanField(
        default=True, help_text="Project-managers and team-members are allowed to edit this study.",
    )

    COPY_NAME = "studies"
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
        return Study.objects.create(**attrs)

    @classmethod
    @transaction.atomic
    def copy_across_assessment(cls, studies, assessment, cw=None, copy_rob=False):

        # copy selected studies from one assessment to another.
        if cw is None:
            cw = collections.defaultdict(dict)

        # assert all studies come from a single assessment
        source_assessment = (
            Assessment.objects.filter(references__in=studies)
            .distinct()
            .values_list("id", flat=True)
        )
        if len(source_assessment) != 1:
            raise ValueError("Studies must come from the same assessment")
        source_assessment = source_assessment[0]
        cw[Assessment.COPY_NAME][source_assessment] = assessment.id

        # copy studies; flag if any epi-meta studies exist
        any_epi_meta = False
        for study in studies:
            logger.info(f"Copying study {study.id} to assessment {assessment.id}")

            # get child-types and copy
            children = []

            if copy_rob:
                children.extend(list(study.riskofbiases.all().order_by("id")))

            if study.bioassay:
                children.extend(list(study.experiments.all().order_by("id")))

            if study.epi:
                children.extend(list(study.study_populations.all().order_by("id")))

            if study.in_vitro:
                children.extend(
                    itertools.chain(
                        study.ivchemicals.all().order_by("id"),
                        study.ivcelltypes.all().order_by("id"),
                        study.ivexperiments.all().order_by("id"),
                    )
                )

            if study.epi_meta:
                any_epi_meta = True
                children.extend(list(study.meta_protocols.all().order_by("id")))

            # copy study and references
            study._copy_across_assessment(cw)

            for child in children:
                child.copy_across_assessments(cw)

        # Copy epimeta.SingleResult after copying studies because to ensure
        # Study clones have already been created.
        if any_epi_meta:
            logger.info("Copying epi results")
            SingleResult = apps.get_model("epimeta", "SingleResult")
            results = SingleResult.objects.filter(
                meta_result__protocol__study__in=studies
            ).order_by("id")
            for result in results:
                result.copy_across_assessments(cw)

        return cw

    def _copy_across_assessment(self, cw):
        # copy reference and identifiers
        # (except RIS which is assessment-specific)
        ref = self.reference_ptr
        idents = ref.identifiers.filter(database__in=[0, 1, 2]).values_list("id", flat=True)
        ref.id = None
        ref.assessment_id = cw[Assessment.COPY_NAME][self.assessment_id]
        ref.save()
        ref.identifiers.add(*idents)

        # associate reference w/ manually added search else it'll be designated an
        # orphan reference which could potentially be deleted by users.
        manual_search = Search.objects.get_manually_added(ref.assessment_id)
        manual_search.references.add(ref)

        # copy study
        old_id = self.id
        self.id = None
        self.reference_ptr = ref
        self.assessment_id = cw[Assessment.COPY_NAME][self.assessment_id]
        self.save()

        # save self to crosswalk
        cw[self.COPY_NAME][old_id] = self.id

    def clean(self):
        pk_exclusion = {}
        errors = {}
        if self.pk:
            pk_exclusion["pk"] = self.pk
        if (
            Study.objects.filter(assessment=self.assessment, short_citation=self.short_citation)
            .exclude(**pk_exclusion)
            .count()
            > 0
        ):
            errors["short_citation"] = ASSESSMENT_UNIQUE_MESSAGE
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.short_citation

    def get_absolute_url(self):
        return reverse("study:detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("study:update", args=[str(self.pk)])

    def get_final_rob_url(self):
        try:
            return self.get_final_rob().get_final_url()
        except ObjectDoesNotExist:
            raise Http404("Final RoB does not exist")

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

    def get_study_type(self):
        types = []
        for field in self.STUDY_TYPE_FIELDS:
            if getattr(self, field):
                types.append(field)
        return types

    @staticmethod
    def flat_complete_header_row():
        return (
            "study-id",
            "study-url",
            "study-short_citation",
            "study-full_citation",
            "study-coi_reported",
            "study-coi_details",
            "study-funding_source",
            "study-bioassay",
            "study-epi",
            "study-epi_meta",
            "study-in_vitro",
            "study-study_identifier",
            "study-contact_author",
            "study-ask_author",
            "study-summary",
            "study-editable",
            "study-published",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["url"],
            ser["short_citation"],
            ser["full_citation"],
            ser["coi_reported"],
            ser["coi_details"],
            ser["funding_source"],
            ser["bioassay"],
            ser["epi"],
            ser["epi_meta"],
            ser["in_vitro"],
            ser["study_identifier"],
            ser["contact_author"],
            ser["ask_author"],
            cleanHTML(ser["summary"]),
            ser["editable"],
            ser["published"],
        )

    @staticmethod
    def get_docx_template_context(assessment, queryset):
        studies = [SerializerHelper.get_serialized(study, json=False) for study in queryset]
        return {
            "assessment": AssessmentSerializer().to_representation(assessment),
            "studies": studies,
        }

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
        except MultipleObjectsReturned:
            raise ObjectDoesNotExist(f'Multiple active final RoB "{self}", expecting one')

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
            .prefetch_related("identifiers", "searches", "riskofbiases__scores__metric__domain",)
            .first()
        )

    def get_study(self):
        return self

    def user_can_edit_study(self, assessment, user) -> bool:
        perms = assessment.get_permissions()
        return perms.can_edit_study(self, user)

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
