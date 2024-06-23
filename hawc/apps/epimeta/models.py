import json

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from reversion import revisions as reversion

from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper
from ..epi.models import AdjustmentFactor, Criteria, ResultMetric
from . import constants, managers


class MetaProtocol(models.Model):
    objects = managers.MetaProtocolManager()

    study = models.ForeignKey(
        "study.Study", on_delete=models.CASCADE, related_name="meta_protocols"
    )
    name = models.CharField(verbose_name="Protocol name", max_length=128)
    protocol_type = models.PositiveSmallIntegerField(
        choices=constants.MetaProtocol, default=constants.MetaProtocol.META
    )
    lit_search_strategy = models.PositiveSmallIntegerField(
        verbose_name="Literature search strategy",
        choices=constants.MetaLitSearch,
        default=constants.MetaLitSearch.SYSTEMATIC,
    )
    lit_search_notes = models.TextField(verbose_name="Literature search notes", blank=True)
    lit_search_start_date = models.DateField(
        verbose_name="Literature search start-date", blank=True, null=True
    )
    lit_search_end_date = models.DateField(
        verbose_name="Literature search end-date", blank=True, null=True
    )
    total_references = models.PositiveIntegerField(
        verbose_name="Total number of references found",
        help_text="References identified through initial literature-search "
        "before application of inclusion/exclusion criteria",
        blank=True,
        null=True,
    )
    inclusion_criteria = models.ManyToManyField(
        Criteria, related_name="meta_inclusion_criteria", blank=True
    )
    exclusion_criteria = models.ManyToManyField(
        Criteria, related_name="meta_exclusion_criteria", blank=True
    )
    total_studies_identified = models.PositiveIntegerField(
        verbose_name="Total number of studies identified",
        help_text="Total references identified for inclusion after application "
        "of literature review and screening criteria",
    )
    notes = models.TextField(blank=True)

    BREADCRUMB_PARENT = "study"

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.study.get_assessment()

    def get_absolute_url(self):
        return reverse("meta:protocol_detail", args=(self.pk,))

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode, from_cache=False)

    def get_study(self):
        return self.study


class MetaResult(models.Model):
    objects = managers.MetaResultManager()

    protocol = models.ForeignKey(MetaProtocol, on_delete=models.CASCADE, related_name="results")
    label = models.CharField(max_length=128)
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
        "(ex: Figure 1, Table 2, etc.)",
    )
    health_outcome = models.CharField(max_length=128)
    health_outcome_notes = models.TextField(blank=True)
    exposure_name = models.CharField(max_length=128)
    exposure_details = models.TextField(blank=True)
    number_studies = models.PositiveSmallIntegerField()
    metric = models.ForeignKey(ResultMetric, on_delete=models.CASCADE)
    statistical_notes = models.TextField(blank=True)
    n = models.PositiveIntegerField(help_text="Number of individuals included from all analyses")
    estimate = models.FloatField()
    heterogeneity = models.CharField(max_length=256, blank=True)
    lower_ci = models.FloatField(
        verbose_name="Lower CI",
        help_text="Numerical value for lower-confidence interval",
    )
    upper_ci = models.FloatField(
        verbose_name="Upper CI",
        help_text="Numerical value for upper-confidence interval",
    )
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name="Confidence Interval (CI)",
        help_text="A 95% CI is written as 0.95.",
    )
    adjustment_factors = models.ManyToManyField(
        AdjustmentFactor,
        help_text="All factors which were included in final model",
        related_name="meta_adjustments",
        blank=True,
    )
    notes = models.TextField(blank=True)

    BREADCRUMB_PARENT = "protocol"

    class Meta:
        ordering = ("label",)

    def __str__(self):
        return self.label

    def get_assessment(self):
        return self.protocol.get_assessment()

    def get_absolute_url(self):
        return reverse("meta:result_detail", args=(self.pk,))

    @property
    def estimate_formatted(self):
        txt = "-"
        if self.estimate:
            txt = str(self.estimate)
        if self.lower_ci and self.upper_ci:
            txt += f" ({self.lower_ci}, {self.upper_ci})"
        return txt

    @classmethod
    def delete_caches(cls, pks):
        SerializerHelper.delete_caches(cls, pks)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @staticmethod
    def get_qs_json(queryset, json_encode=True):
        results = [result.get_json(json_encode=False) for result in queryset]
        if json_encode:
            return json.dumps(results, cls=HAWCDjangoJSONEncoder)
        else:
            return results

    def get_study(self):
        if self.protocol is not None:
            return self.protocol.get_study()


class SingleResult(models.Model):
    objects = managers.SingleResultManager()

    meta_result = models.ForeignKey(
        MetaResult, on_delete=models.CASCADE, related_name="single_results"
    )
    study = models.ForeignKey(
        "study.Study",
        on_delete=models.SET_NULL,
        related_name="single_results",
        blank=True,
        null=True,
    )
    exposure_name = models.CharField(
        max_length=128,
        help_text="Enter a descriptive-name for the single study result "
        '(e.g., "Smith et al. 2000, obese-males")',
    )
    weight = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="For meta-analysis, enter the fraction-weight assigned for "
        "each result (leave-blank for pooled analyses)",
    )
    n = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Enter the number of observations for this result",
    )
    estimate = models.FloatField(
        blank=True,
        null=True,
        help_text="Enter the numerical risk-estimate presented for this result",
    )
    lower_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Lower CI",
        help_text="Numerical value for lower-confidence interval",
    )
    upper_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Upper CI",
        help_text="Numerical value for upper-confidence interval",
    )
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name="Confidence Interval (CI)",
        help_text="A 95% CI is written as 0.95.",
    )
    notes = models.TextField(blank=True)

    BREADCRUMB_PARENT = "meta_result"

    class Meta:
        ordering = ("exposure_name",)

    def __str__(self):
        return self.exposure_name

    @property
    def estimate_formatted(self):
        txt = "-"
        if self.estimate:
            txt = str(self.estimate)
        if self.lower_ci and self.upper_ci:
            txt += f" ({self.lower_ci}, {self.upper_ci})"
        return txt

    def get_study(self):
        if self.meta_result is not None:
            return self.meta_result.get_study()


reversion.register(MetaProtocol, follow=("inclusion_criteria", "exclusion_criteria"))
reversion.register(MetaResult, follow=("adjustment_factors", "single_results"))
reversion.register(SingleResult)
