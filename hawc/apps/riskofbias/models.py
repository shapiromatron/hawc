import json
import logging
from typing import Dict, List, Tuple

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from reversion import revisions as reversion

from ..assessment.models import Assessment
from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper, cleanHTML
from ..common.models import get_flavored_text
from ..myuser.models import HAWCUser
from ..study.models import Study
from . import managers


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
    sort_order = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = "riskofbiasdomains"
    BREADCRUMB_PARENT = "assessment"

    class Meta:
        unique_together = ("assessment", "name")
        ordering = ("assessment", "sort_order")

    def clean(self):
        if self.sort_order is None:
            self.sort_order = len(self.assessment.rob_domains.all())

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse("riskofbias:arob_detail", args=(self.assessment_id,))

    @classmethod
    def build_default(cls, assessment):
        """
        Construct default risk of bias domains/metrics for an assessment.
        The risk of bias domains and metrics are those defined by NTP/OHAT
        protocols for risk of bias
        """
        if settings.HAWC_FLAVOR == "PRIME":
            fixture = "ohat_study_quality_defaults.json"
        elif settings.HAWC_FLAVOR == "EPA":
            fixture = "iris_study_quality_defaults.json"
        else:
            raise ValueError("Unknown HAWC flavor")

        fn = settings.PROJECT_PATH / f"apps/riskofbias/fixtures/{fixture}"
        objects = json.loads(fn.read_text())
        for sort_order, domain in enumerate(objects["domains"], start=1):
            d = RiskOfBiasDomain.objects.create(
                assessment=assessment,
                sort_order=sort_order,
                name=domain["name"],
                description=domain["description"],
            )
            RiskOfBiasMetric.build_metrics_for_one_domain(d, domain["metrics"])

    def copy_across_assessments(self, cw):
        children = list(self.metrics.all().order_by("id"))
        old_id = self.id
        self.id = None
        self.assessment_id = cw[Assessment.COPY_NAME][self.assessment_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)


class RiskOfBiasMetric(models.Model):
    objects = managers.RiskOfBiasMetricManager()

    RESPONSES_OHAT = 0
    RESPONSES_EPA = 1
    RESPONSES_NONE = 2

    RESPONSES_CHOICES = (
        (RESPONSES_OHAT, "OHAT"),
        (RESPONSES_EPA, "EPA"),
        (RESPONSES_NONE, "No scores"),
    )

    RESPONSES_VALUES = {
        RESPONSES_OHAT: [17, 16, 15, 12, 14, 10],
        RESPONSES_EPA: [27, 26, 25, 24, 37, 36, 35, 34, 22, 20],
        RESPONSES_NONE: [],
    }

    def get_default_responses():
        if settings.HAWC_FLAVOR == "PRIME":
            return 0
        elif settings.HAWC_FLAVOR == "EPA":
            return 1
        else:
            raise ValueError("Unknown HAWC flavor")

    domain = models.ForeignKey(RiskOfBiasDomain, on_delete=models.CASCADE, related_name="metrics")
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=50, blank=True)
    description = models.TextField(
        blank=True, help_text="HTML text describing scoring of this field."
    )
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
    responses = models.PositiveSmallIntegerField(
        choices=RESPONSES_CHOICES, default=get_default_responses
    )
    sort_order = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = "riskofbiasmetrics"
    BREADCRUMB_PARENT = "domain"

    class Meta:
        ordering = ("domain", "sort_order")

    def clean(self):
        if self.sort_order is None:
            self.sort_order = len(self.domain.metrics.all())

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.domain.get_assessment()

    def get_absolute_url(self):
        return reverse("riskofbias:arob_detail", args=(self.domain.assessment_id,))

    def get_response_values(self):
        return self.RESPONSES_VALUES[self.responses]

    @classmethod
    def build_metrics_for_one_domain(cls, domain, metrics):
        """
        Build multiple risk of bias metrics given a domain django object and a
        list of python dictionaries for each metric.
        """
        objs = []
        for sort_order, metric in enumerate(metrics, start=1):
            obj = RiskOfBiasMetric(sort_order=sort_order, **metric)
            obj.domain = domain
            objs.append(obj)
        RiskOfBiasMetric.objects.bulk_create(objs)

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.domain_id = cw[RiskOfBiasDomain.COPY_NAME][self.domain_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


class RiskOfBias(models.Model):
    objects = managers.RiskOfBiasManager()

    study = models.ForeignKey(
        "study.Study", on_delete=models.CASCADE, related_name="riskofbiases", null=True
    )
    final = models.BooleanField(default=False, db_index=True)
    author = models.ForeignKey(HAWCUser, on_delete=models.CASCADE, related_name="riskofbiases")
    active = models.BooleanField(default=False, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = "riskofbiases"
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
        return reverse("riskofbias:arob_reviewers", args=[self.study.assessment_id])

    def get_edit_url(self):
        return reverse("riskofbias:rob_update", args=[self.pk])

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @staticmethod
    def get_qs_json(queryset, json_encode=True):
        robs = [rob.get_json(json_encode=False) for rob in queryset]
        if json_encode:
            return json.dumps(robs, cls=HAWCDjangoJSONEncoder)
        else:
            return robs

    def update_scores(self, assessment):
        """Sync RiskOfBiasScore for this study based on assessment requirements.

        Metrics may change based on study type and metric requirements by study
        type. This method is called via signals when the study type changes,
        or when a metric is altered.  RiskOfBiasScore are created/deleted as
        needed.
        """
        metrics = RiskOfBiasMetric.objects.get_required_metrics(
            assessment, self.study
        ).prefetch_related("scores")
        scores = self.scores.all()
        # add any scores that are required and not currently created
        for metric in metrics:
            if not (metric.scores.all() & scores):
                logging.info(f"Creating score: {self.study}->{metric}")
                RiskOfBiasScore.objects.create(riskofbias=self, metric=metric)
        # delete any scores that are no longer required
        for score in scores:
            if score.metric not in metrics:
                logging.info(f"Deleting score: {self.study}->{score.metric}")
                score.delete()

    def build_scores(self, assessment, study):
        scores = [
            RiskOfBiasScore(riskofbias=self, metric=metric)
            for metric in RiskOfBiasMetric.objects.get_required_metrics(assessment, study)
        ]
        RiskOfBiasScore.objects.bulk_create(scores)

    def activate(self):
        self.active = True
        self.save()

    def deactivate(self):
        self.active = False
        self.save()

    @property
    def is_complete(self):
        """
        The rich text editor used for notes input adds HTML tags even if input
        is empty, so HTML needs to be stripped out.
        """
        return all(
            [
                len(strip_tags(score.notes)) > 0
                for score in self.scores.all()
                if score.score not in RiskOfBiasScore.NA_SCORES
            ]
        )

    @property
    def study_reviews_complete(self):
        return all([rob.is_complete for rob in self.study.get_active_robs(with_final=False)])

    @staticmethod
    def copy_riskofbias(copy_to_assessment, copy_from_assessment):
        # delete existing study quality metrics and domains
        copy_to_assessment.rob_domains.all().delete()

        # copy domains and metrics to assessment
        for domain in copy_from_assessment.rob_domains.all():
            metrics = list(domain.metrics.all())  # force evaluation
            domain.id = None
            domain.assessment = copy_to_assessment
            domain.save()
            for metric in metrics:
                metric.id = None
                metric.domain = domain
                metric.save()

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @staticmethod
    def flat_header_row(final_only: bool = True):
        col = ["rob-id", "rob-created", "rob-last_updated"]
        if not final_only:
            col[1:1] = ["rob-active", "rob-final", "rob-author_id", "rob-author_name"]
        return col

    @staticmethod
    def flat_data_row(ser, final_only: bool = True):
        row = [ser["id"], ser["created"], ser["last_updated"]]
        if not final_only:
            row[1:1] = [
                ser["active"],
                ser["final"],
                ser["author"]["id"],
                ser["author"]["full_name"],
            ]
        return row

    def copy_across_assessments(self, cw):
        children = list(self.scores.all().order_by("id"))
        old_id = self.id
        self.id = None
        self.study_id = cw[Study.COPY_NAME][self.study_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)

    @classmethod
    def get_dp_export(
        cls, assessment_id: int, study_ids: List[int], data_type: str
    ) -> Tuple[Dict, Dict]:
        """
        Given an assessment, a list of studies, and a data type, return all the data required to
        build a data pivot risk of bias export for only active, final data.

        Args:
            assessment_id (int): An assessment identifier
            study_ids (List[int]): A list of studies ids to include
            data_type (str): The data type to use; one of {"animal", "epi", "invitro"}

        Returns:
            Tuple[Dict, Dict]: A {metric_id: header_name} dict for building headers, and a
                {(study_id, metric_id): text} dict for building rows
        """
        data_types = {"animal", "epi", "invitro"}
        if data_type not in data_types:
            raise ValueError(f"Unsupported data type {data_type}; expected {data_types}")

        filters = dict(domain__assessment_id=assessment_id)
        if data_type == "animal":
            filters["required_animal"] = True
        elif data_type == "epi":
            filters["required_epi"] = True
        elif data_type == "invitro":
            filters["required_invitro"] = True

        # return headers
        metric_qs = list(
            RiskOfBiasMetric.objects.filter(**filters).select_related("domain").order_by("id")
        )
        header_map = {metric.id: "" for metric in metric_qs}
        for metric in metric_qs:
            if metric.domain.is_overall_confidence:
                text = "Overall study confidence"
            elif metric.use_short_name:
                text = f"RoB ({metric.short_name})"
            else:
                text = f"RoB ({metric.domain.name}: {metric.name})"
            header_map[metric.id] = text

        # return data
        metric_ids = list(header_map.keys())
        scores = RiskOfBiasScore.objects.filter(
            metric__in=metric_ids,
            riskofbias__study__in=study_ids,
            riskofbias__final=True,
            riskofbias__active=True,
            is_default=True,
        ).prefetch_related("riskofbias")
        default_value = '{"sortValue": -1, "display": "N/A"}'
        scores_map = {(score.riskofbias.study_id, score.metric_id): score for score in scores}
        for metric_id in metric_ids:
            for study_id in study_ids:
                key = (study_id, metric_id)
                if key in scores_map and not isinstance(scores_map[key], str):
                    # convert values in our map to a str-based JSON
                    score = scores_map[key]
                    content = json.dumps(
                        {"sortValue": score.score, "display": score.get_score_display()}
                    )

                    # special case for N/A
                    if score.score in RiskOfBiasScore.NA_SCORES:
                        content = default_value

                    scores_map[key] = content

                else:
                    scores_map[key] = default_value

        return header_map, scores_map

    def get_override_options(self) -> Dict:
        """Get risk of bias override options and overrides

        Returns:
            Dict: A dictionary of metadata and choices
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


def build_default_rob_score():
    if settings.HAWC_FLAVOR == "PRIME":
        return 12
    elif settings.HAWC_FLAVOR == "EPA":
        return 22
    else:
        raise ValueError("Unknown HAWC flavor")


class RiskOfBiasScore(models.Model):
    objects = managers.RiskOfBiasScoreManager()

    RISK_OF_BIAS_SCORE_CHOICES = (
        (10, "Not applicable"),
        (12, "Not reported"),
        (14, "Definitely high risk of bias"),
        (15, "Probably high risk of bias"),
        (16, "Probably low risk of bias"),
        (17, "Definitely low risk of bias"),
        (20, "Not applicable"),
        (22, "Not reported"),
        (24, "Critically deficient"),
        (25, "Deficient"),
        (26, "Adequate"),
        (27, "Good"),
        (34, "Uninformative"),
        (35, "Low confidence"),
        (36, "Medium confidence"),
        (37, "High confidence"),
    )

    RISK_OF_BIAS_SCORE_CHOICES_MAP = {k: v for k, v in RISK_OF_BIAS_SCORE_CHOICES}

    NA_SCORES = (10, 20)

    SCORE_SYMBOLS = {
        10: "N/A",
        12: "NR",
        14: "--",
        15: "-",
        16: "+",
        17: "++",
        20: "N/A",
        22: "NR",
        24: "--",
        25: "-",
        26: "+",
        27: "++",
        34: "--",
        35: "-",
        36: "+",
        37: "++",
    }

    SCORE_SHADES = {
        10: "#E8E8E8",
        12: "#FFCC00",
        14: "#CC3333",
        15: "#FFCC00",
        16: "#6FFF00",
        17: "#00CC00",
        20: "#E8E8E8",
        22: "#FFCC00",
        24: "#CC3333",
        25: "#FFCC00",
        26: "#6FFF00",
        27: "#00CC00",
        34: "#CC3333",
        35: "#FFCC00",
        36: "#6FFF00",
        37: "#00CC00",
    }

    BIAS_DIRECTION_UNKNOWN = 0
    BIAS_DIRECTION_UP = 1
    BIAS_DIRECTION_DOWN = 2
    BIAS_DIRECTION_CHOICES = (
        (BIAS_DIRECTION_UNKNOWN, "not entered/unknown"),
        (BIAS_DIRECTION_UP, "⬆ (away from null)"),
        (BIAS_DIRECTION_DOWN, "⬇ (towards null)"),
    )

    TEXT_CLEANUP_FIELDS = (
        "score",
        "notes",
    )

    riskofbias = models.ForeignKey(RiskOfBias, on_delete=models.CASCADE, related_name="scores")
    metric = models.ForeignKey(RiskOfBiasMetric, on_delete=models.CASCADE, related_name="scores")
    is_default = models.BooleanField(default=True)
    label = models.CharField(max_length=128, blank=True)
    score = models.PositiveSmallIntegerField(
        choices=RISK_OF_BIAS_SCORE_CHOICES, default=build_default_rob_score
    )
    bias_direction = models.PositiveSmallIntegerField(
        choices=BIAS_DIRECTION_CHOICES,
        default=BIAS_DIRECTION_UNKNOWN,
        help_text="Judgment of direction of bias (⬆ = away from null, ⬇ = towards null); only add entry if important to show in visuals",
    )
    notes = models.TextField(blank=True)

    COPY_NAME = "riskofbiasscores"

    class Meta:
        ordering = ("metric", "id")

    def __str__(self):
        return f"{self.riskofbias} {self.metric}"

    def get_assessment(self):
        return self.metric.get_assessment()

    @staticmethod
    def flat_complete_header_row():
        return (
            "rob-domain_id",
            "rob-domain_name",
            "rob-domain_description",
            "rob-metric_id",
            "rob-metric_name",
            "rob-metric_description",
            "rob-score_id",
            "rob-score_is_default",
            "rob-score_label",
            "rob-score_score",
            "rob-score_description",
            "rob-score_bias_direction",
            "rob-score_notes",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["metric"]["domain"]["id"],
            ser["metric"]["domain"]["name"],
            ser["metric"]["domain"]["description"],
            ser["metric"]["id"],
            ser["metric"]["name"],
            ser["metric"]["description"],
            ser["id"],
            ser["is_default"],
            ser["label"],
            ser["score"],
            ser["score_description"],
            ser["bias_direction"],
            cleanHTML(ser["notes"]),
        )

    @property
    def score_symbol(self):
        return self.SCORE_SYMBOLS[self.score]

    @property
    def score_shade(self):
        return self.SCORE_SHADES[self.score]

    @classmethod
    def delete_caches(cls, ids):
        id_lists = [
            (score.riskofbias.id, score.riskofbias.study_id)
            for score in cls.objects.filter(id__in=ids)
        ]
        rob_ids, study_ids = list(zip(*id_lists))
        RiskOfBias.delete_caches(rob_ids)
        Study.delete_caches(study_ids)

    def copy_across_assessments(self, cw):
        # TODO - add overrides
        old_id = self.id
        self.id = None
        self.riskofbias_id = cw[RiskOfBias.COPY_NAME][self.riskofbias_id]
        self.metric_id = cw[RiskOfBiasMetric.COPY_NAME][self.metric_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


class RiskOfBiasScoreOverrideObject(models.Model):
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
        cts = RiskOfBiasScoreOverrideObject.objects.values_list(
            "content_type", flat=True
        ).distinct()

        deletions = []
        for ct in cts:
            RelatedClass = ContentType.objects.get_for_id(ct).model_class()
            all_ids = cls.objects.filter(content_type=ct).values_list("object_id", flat=True)
            matched_ids = RelatedClass.objects.filter(id__in=all_ids).values_list("id", flat=True)
            deleted_ids = list(set(all_ids) - set(matched_ids))
            if deleted_ids:
                deletions.extend(
                    list(cls.objects.filter(content_type=ct, object_id__in=deleted_ids))
                )

        message = ""
        if deletions:
            message = "\n".join([str(item) for item in deletions])
            ids_to_delete = [item.id for item in deletions]
            if delete:
                message = f"Deleting orphaned RiskOfBiasScoreOverrideObjects:\n{message}"
                cls.objects.filter(id__in=ids_to_delete).delete()
            else:
                message = f"Found orphaned RiskOfBiasScoreOverrideObjects:\n{message}"

        return message


DEFAULT_QUESTIONS_OHAT = 1
DEFAULT_QUESTIONS_EPA = 2

RESPONSES_OHAT = 0
RESPONSES_EPA = 1


class RiskOfBiasAssessment(models.Model):
    objects = managers.RiskOfBiasAssessmentManager()

    DEFAULT_QUESTIONS_CHOICES = (
        (DEFAULT_QUESTIONS_OHAT, "OHAT"),
        (DEFAULT_QUESTIONS_EPA, "EPA"),
    )

    def get_default_default_questions():
        if settings.HAWC_FLAVOR == "PRIME":
            return DEFAULT_QUESTIONS_OHAT
        elif settings.HAWC_FLAVOR == "EPA":
            return DEFAULT_QUESTIONS_EPA
        else:
            raise ValueError("Unknown HAWC flavor")

    RESPONSES_CHOICES = (
        (RESPONSES_OHAT, "OHAT"),
        (RESPONSES_EPA, "EPA"),
    )

    def get_default_responses():
        if settings.HAWC_FLAVOR == "PRIME":
            return RESPONSES_OHAT
        elif settings.HAWC_FLAVOR == "EPA":
            return RESPONSES_EPA
        else:
            raise ValueError("Unknown HAWC flavor")

    assessment = models.OneToOneField(
        Assessment, on_delete=models.CASCADE, related_name="rob_settings"
    )
    number_of_reviewers = models.PositiveSmallIntegerField(default=1)
    help_text = models.TextField(
        default="Instructions for reviewers completing assessments",
        help_text="Detailed instructions for completing risk of bias assessments.",
    )
    default_questions = models.PositiveSmallIntegerField(
        choices=DEFAULT_QUESTIONS_CHOICES,
        default=get_default_default_questions,
        verbose_name="Default questions",
        help_text="If no questions exist, which default questions should be used? If questions already exist, changing this will have no impact.",
    )
    responses = models.PositiveSmallIntegerField(
        choices=RESPONSES_CHOICES,
        default=get_default_responses,
        verbose_name="Question responses",
        help_text="Why responses should be used to answering questions:",
    )

    COPY_NAME = "riskofbiasassessments"
    BREADCRUMB_PARENT = "assessment"

    def get_absolute_url(self):
        return reverse("riskofbias:arob_reviewers", args=[self.assessment_id])

    @classmethod
    def build_default(cls, assessment):
        RiskOfBiasAssessment.objects.create(
            assessment=assessment,
            help_text=get_flavored_text("riskofbias__riskofbiasassessment_help_text_default"),
        )

    def get_rob_response_values(self):
        # get valid RiskOfBiasScore response options given responses selection
        if self.responses == RESPONSES_OHAT:
            return [17, 16, 15, 12, 14, 10]
        elif self.responses == RESPONSES_EPA:
            return [27, 26, 25, 24, 37, 36, 35, 34, 22, 20]
        else:
            raise ValueError(f"Unknown responses: {self.responses}")

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        new_assessment_id = cw[Assessment.COPY_NAME][self.assessment_id]
        self.assessment_id = new_assessment_id
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


reversion.register(RiskOfBiasDomain)
reversion.register(RiskOfBiasMetric)
reversion.register(RiskOfBias)
reversion.register(RiskOfBiasScore)
reversion.register(RiskOfBiasScoreOverrideObject)
