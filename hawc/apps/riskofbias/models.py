import logging
from itertools import product
from textwrap import dedent

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.urls import reverse
from django.utils.html import strip_tags
from reversion import revisions as reversion

from ..assessment.models import Assessment
from ..common.helper import SerializerHelper
from ..myuser.models import HAWCUser
from ..study.models import Study
from . import constants, managers

logger = logging.getLogger(__name__)


class RiskOfBiasDomain(models.Model):
    objects = managers.RiskOfBiasDomainManager()

    assessment = models.ForeignKey(
        "assessment.Assessment", on_delete=models.CASCADE, related_name="rob_domains"
    )
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_overall_confidence = models.BooleanField(
        default=False,
        verbose_name="Overall confidence?",
        help_text="Is this domain for overall confidence?",
    )
    sort_order = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        unique_together = ("assessment", "name")
        ordering = ("assessment", "sort_order")

    def clean(self):
        if self.sort_order is None:
            self.sort_order = len(self.assessment.rob_domains.all()) + 1

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse("riskofbias:arob_detail", args=(self.assessment_id,))


class RiskOfBiasMetric(models.Model):
    objects = managers.RiskOfBiasMetricManager()

    domain = models.ForeignKey(RiskOfBiasDomain, on_delete=models.CASCADE, related_name="metrics")
    name = models.CharField(max_length=256, help_text="Complete name of metric.")
    short_name = models.CharField(
        max_length=50, blank=True, help_text="Short name, may be used in visualizations."
    )
    key = models.CharField(
        max_length=8,
        blank=True,
        help_text="A unique identifier if it is from a standard protocol or procedure; can be used to match metrics across assessments.",
    )
    description = models.TextField(
        blank=True, help_text="Detailed instructions for how to apply this metric."
    )
    responses = models.PositiveSmallIntegerField(choices=constants.RiskOfBiasResponses)
    required_animal = models.BooleanField(
        default=True,
        verbose_name="Required for bioassay?",
        help_text="Is this metric required for animal bioassay studies?<br/><b>CAUTION:</b> Removing requirement will destroy all bioassay responses previously entered for this metric.",
    )
    required_epi = models.BooleanField(
        default=True,
        verbose_name="Required for epidemiology?",
        help_text="Is this metric required for human epidemiological studies?<br/><b>CAUTION:</b> Removing requirement will destroy all epi responses previously entered for this metric.",
    )
    required_invitro = models.BooleanField(
        default=True,
        verbose_name="Required for in-vitro?",
        help_text="Is this metric required for in-vitro studies?<br/><b>CAUTION:</b> Removing requirement will destroy all in-vitro responses previously entered for this metric.",
    )
    hide_description = models.BooleanField(
        default=False,
        verbose_name="Hide description?",
        help_text="Hide the description on reports?",
    )
    use_short_name = models.BooleanField(
        default=False,
        verbose_name="Use the short name?",
        help_text="Use the short name in visualizations?",
    )
    sort_order = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "domain"

    class Meta:
        ordering = ("domain", "sort_order")

    def clean(self):
        if self.sort_order is None:
            self.sort_order = len(self.domain.metrics.all()) + 1

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.domain.get_assessment()

    def get_absolute_url(self):
        return reverse("riskofbias:arob_detail", args=(self.domain.assessment_id,))

    def get_response_values(self):
        return constants.RESPONSES_VALUES[self.responses]

    def get_default_response(self):
        return constants.RESPONSES_VALUES_DEFAULT[self.responses]

    def build_score(self, riskofbias: "RiskOfBias", is_default: bool):
        return RiskOfBiasScore(
            riskofbias=riskofbias,
            metric=self,
            score=constants.RESPONSES_VALUES_DEFAULT[self.responses],
            is_default=is_default,
        )

    @transaction.atomic
    def sync_score_existence(self):
        """Create/delete scores based on current metric requirements."""
        actual_ids = set(self.scores.all().values_list("riskofbias_id", flat=True))

        expected = {}
        expected_ids = set()
        robs = RiskOfBias.objects.get_required_robs_for_metric(self)
        if robs:
            expected = robs.in_bulk()
            expected_ids = set(expected.keys())

        create_ids = expected_ids - actual_ids
        if create_ids:
            scores = [self.build_score(expected[rob_id], True) for rob_id in create_ids]
            RiskOfBiasScore.objects.bulk_create(scores)

        delete_ids = actual_ids - expected_ids
        if delete_ids:
            RiskOfBiasScore.objects.filter(metric=self, riskofbias_id__in=delete_ids).delete()

    @classmethod
    @transaction.atomic
    def sync_scores_for_study(cls, study: Study):
        """Create/delete scores based on current study requirements."""
        robs = study.riskofbiases.all().in_bulk()
        rob_ids = robs.keys()
        metrics = cls.objects.get_required_metrics(study).in_bulk()

        expected_ids = set(product(metrics.keys(), rob_ids))
        actual_ids = set(
            RiskOfBiasScore.objects.filter(riskofbias__in=rob_ids).values_list(
                "metric_id", "riskofbias_id"
            )
        )

        create_ids = expected_ids - actual_ids
        if create_ids:
            scores = [
                metrics[metric_id].build_score(robs[rob_id], True)
                for metric_id, rob_id in create_ids
            ]
            RiskOfBiasScore.objects.bulk_create(scores)

        delete_ids = actual_ids - expected_ids
        if delete_ids:
            for metric_id, rob_id in delete_ids:
                # may be more than one if there are overrides
                RiskOfBiasScore.objects.filter(metric=metric_id, riskofbias=rob_id).delete()
                logger.info(f"Study {study.id} change; deleted {metric_id=}; {rob_id=}")


class RiskOfBias(models.Model):
    objects = managers.RiskOfBiasManager()

    study = models.ForeignKey("study.Study", on_delete=models.CASCADE, related_name="riskofbiases")
    final = models.BooleanField(default=False, db_index=True)
    author = models.ForeignKey(HAWCUser, on_delete=models.CASCADE, related_name="riskofbiases")
    active = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study"

    class Meta:
        verbose_name_plural = "Risk of Biases"
        ordering = ("final", "id")

    def __str__(self):
        return f"{self.study.short_citation} (Risk of bias)"

    def get_assessment(self):
        return self.study.get_assessment()

    def get_final_url(self):
        return reverse("riskofbias:rob_detail", args=[self.study_id])

    def get_absolute_url(self):
        return reverse("riskofbias:rob_assignments", args=[self.study.assessment_id])

    def get_edit_url(self):
        return reverse("riskofbias:rob_update", args=[self.pk])

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def build_scores(self, assessment, study):
        scores = [
            metric.build_score(riskofbias=self, is_default=True)
            for metric in RiskOfBiasMetric.objects.get_required_metrics(study)
        ]
        RiskOfBiasScore.objects.bulk_create(scores)

    def activate(self):
        self.active = True
        self.save()

    def deactivate(self):
        self.active = False
        self.save()

    @property
    def is_complete(self) -> bool:
        """
        A review is complete if all scores either:
        1) have a score not equal to NR (default score when created)
        2) have an NR score, but notes were added
        """
        incomplete = [
            item
            for item in self.scores.all()
            if item.score in constants.NR_SCORES and len(strip_tags(item.notes).strip()) == 0
        ]
        return len(incomplete) == 0

    @property
    def study_reviews_complete(self):
        return all([rob.is_complete for rob in self.study.get_active_robs(with_final=False)])

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    def get_override_options(self) -> dict:
        """Get risk of bias override options and overrides

        Returns:
            dict: A dictionary of metadata and choices
        """
        options = {}

        qs = (
            apps.get_model("animal.Endpoint")
            .objects.filter(animal_group__experiment__study=self.study_id)
            .select_related("animal_group", "animal_group__experiment")
            .order_by("animal_group__experiment_id", "animal_group_id", "id")
        )
        options["animal.endpoint"] = [
            (
                el.id,
                f"{el.animal_group.experiment} → {el.animal_group} → {el}",
                el.get_absolute_url(),
            )
            for el in qs
        ]

        qs = (
            apps.get_model("animal.AnimalGroup")
            .objects.filter(experiment__study=self.study_id)
            .select_related("experiment")
            .order_by("experiment_id", "id")
        )
        options["animal.animalgroup"] = [
            (el.id, f"{el.experiment} → {el}", el.get_absolute_url()) for el in qs
        ]

        qs = (
            apps.get_model("epi.Outcome")
            .objects.filter(study_population__study=self.study_id)
            .select_related("study_population")
            .order_by("study_population_id", "id")
        )
        options["epi.outcome"] = [(el.id, str(el), el.get_absolute_url()) for el in qs]

        qs = (
            apps.get_model("epi.Exposure")
            .objects.filter(study_population__study=self.study_id)
            .select_related("study_population")
            .order_by("study_population_id", "id")
        )
        options["epi.exposure"] = [(el.id, str(el), el.get_absolute_url()) for el in qs]

        qs = (
            apps.get_model("epi.Result")
            .objects.filter(outcome__study_population__study=self.study_id)
            .select_related("outcome", "outcome__study_population")
            .order_by("outcome__study_population_id", "outcome_id", "id")
        )
        options["epi.result"] = [
            (el.id, f"{el.outcome} → {el}", el.get_absolute_url()) for el in qs
        ]

        return options


class RiskOfBiasScore(models.Model):
    objects = managers.RiskOfBiasScoreManager()

    TEXT_CLEANUP_FIELDS = (
        "score",
        "notes",
    )

    riskofbias = models.ForeignKey(RiskOfBias, on_delete=models.CASCADE, related_name="scores")
    metric = models.ForeignKey(RiskOfBiasMetric, on_delete=models.CASCADE, related_name="scores")
    is_default = models.BooleanField(default=True)
    label = models.CharField(max_length=128, blank=True)
    score = models.PositiveSmallIntegerField(choices=constants.SCORE_CHOICES)
    bias_direction = models.PositiveSmallIntegerField(
        choices=constants.BiasDirections,
        default=constants.BiasDirections.BIAS_DIRECTION_UNKNOWN,
        help_text="Judgment of direction of bias (⬆ = away from null, ⬇ = towards null); only add entry if important to show in visuals",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("metric", "id")

    def __str__(self):
        return f"{self.riskofbias} {self.metric}"

    def clean(self):
        # if score is none, set default
        if self.score is None:
            self.score = self.metric.get_default_response()
        # if score not in accepted metric scores, raise error
        if self.score not in self.metric.get_response_values():
            err = f"'{self.get_score_display()}' is not a valid score for this metric."
            raise ValidationError(err)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_assessment(self):
        return self.metric.get_assessment()

    @property
    def score_symbol(self):
        return constants.SCORE_SYMBOLS[self.score]

    @property
    def score_shade(self):
        return constants.SCORE_SHADES[self.score]

    @classmethod
    def delete_caches(cls, ids):
        id_lists = [
            (score.riskofbias.id, score.riskofbias.study_id)
            for score in cls.objects.filter(id__in=ids)
        ]
        rob_ids, study_ids = list(zip(*id_lists, strict=True))
        RiskOfBias.delete_caches(rob_ids)
        Study.delete_caches(study_ids)


class RiskOfBiasScoreOverrideObject(models.Model):
    objects = managers.RiskOfBiasScoreOverrideObjectManager()

    score = models.ForeignKey(
        RiskOfBiasScore, on_delete=models.CASCADE, related_name="overridden_objects"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"id={self.id};score={self.score_id};obj_ct={self.content_type_id};obj_id={self.object_id}"

    def get_content_type_name(self) -> str:
        return f"{self.content_type.app_label}.{self.content_type.model}"

    def get_object_url(self) -> str:
        if self.content_object is None:
            return reverse("404")
        return self.content_object.get_absolute_url()

    def get_object_name(self) -> str:
        if self.content_object is None:
            return f"<deleted {self}>"
        return str(self.content_object)

    @classmethod
    def get_orphan_relations(cls, delete: bool = False) -> str:
        """Determine if any relations are orphaned and optionally delete.

        Args:
            delete (bool, optional): Delete found instances. Defaults to False.

        Returns:
            str: A log message of relations found and what as done.
        """
        message = ""
        deletions = cls.objects.all().orphaned()
        if deletions:
            message = "\n".join([str(item) for item in deletions])
            ids_to_delete = [item.id for item in deletions]
            if delete:
                message = f"Deleting orphaned RiskOfBiasScoreOverrideObjects:\n{message}"
                cls.objects.filter(id__in=ids_to_delete).delete()
            else:
                message = f"Found orphaned RiskOfBiasScoreOverrideObjects:\n{message}"

        return message


class RiskOfBiasAssessment(models.Model):
    objects = managers.RiskOfBiasAssessmentManager()

    assessment = models.OneToOneField(
        Assessment, on_delete=models.CASCADE, related_name="rob_settings"
    )
    number_of_reviewers = models.PositiveSmallIntegerField(default=1)
    help_text = models.TextField(
        default="Instructions for reviewers completing assessments",
        help_text="Detailed instructions for completing risk of bias assessments.",
    )

    BREADCRUMB_PARENT = "assessment"

    def get_absolute_url(self):
        return reverse("riskofbias:rob_assignments", args=(self.id,))

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_default(cls, assessment):
        RiskOfBiasAssessment.objects.create(
            assessment=assessment,
            help_text=dedent(
                """\
                <p>Study evaluation and/or risk of bias can be conducted on studies in HAWC.
                Metrics are organized into different domains. Depending on the study type for
                the study entered in HAWC, different metrics may be required (e.g., some metrics
                may be required for epidemiological studies, while others are required for animal
                bioassay studies). There may also be an overall judgment on the the study.</p>
                <p>The following questions are required for this assessment:</p>"""
            ),
        )


reversion.register(RiskOfBiasDomain)
reversion.register(RiskOfBiasMetric)
reversion.register(RiskOfBias)
reversion.register(RiskOfBiasScore)
reversion.register(RiskOfBiasScoreOverrideObject)
