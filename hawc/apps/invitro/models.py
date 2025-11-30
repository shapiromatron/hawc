from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from reversion import revisions as reversion

from ..animal.models import ConfidenceIntervalsMixin
from ..assessment.models import BaseEndpoint, DSSTox
from ..common.helper import SerializerHelper
from ..common.models import AssessmentRootedTagTree
from . import constants, managers


class IVChemical(models.Model):
    objects = managers.IVChemicalManager()

    study = models.ForeignKey("study.Study", on_delete=models.CASCADE, related_name="ivchemicals")
    name = models.CharField(max_length=128)
    cas = models.CharField(max_length=40, blank=True, verbose_name="Chemical identifier (CAS)")
    dtxsid = models.ForeignKey(
        DSSTox,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="ivchemicals",
        verbose_name="DSSTox substance identifier (DTXSID)",
        help_text=DSSTox.help_text(),
    )
    cas_inferred = models.BooleanField(
        default=False,
        verbose_name="CAS inferred?",
        help_text="Was the correct CAS inferred or incorrect in the original document?",
    )
    cas_notes = models.CharField(max_length=256, verbose_name="CAS determination notes")
    source = models.CharField(max_length=128, verbose_name="Source of chemical")
    purity = models.CharField(
        max_length=32,
        verbose_name="Chemical purity",
        help_text="Ex: >99%, not-reported, etc.",
    )
    purity_confirmed = models.BooleanField(
        default=False, verbose_name="Purity experimentally confirmed"
    )
    purity_confirmed_notes = models.TextField(blank=True)
    dilution_storage_notes = models.TextField(
        help_text="Dilution, storage, and observations such as precipitation should be noted here."
    )

    TEXT_CLEANUP_FIELDS = (
        "name",
        "cas",
        "source",
        "purity",
    )

    BREADCRUMB_PARENT = "study"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("invitro:chemical_detail", args=(self.id,))

    def get_update_url(self):
        return reverse("invitro:chemical_update", args=(self.id,))

    def get_delete_url(self):
        return reverse("invitro:chemical_delete", args=(self.id,))

    def get_assessment(self):
        return self.study.assessment

    @classmethod
    def delete_caches(cls, ids):
        IVEndpoint.delete_caches(
            IVEndpoint.objects.filter(chemical__in=ids).values_list("id", flat=True)
        )

    def get_study(self):
        return self.study


class IVCellType(models.Model):
    objects = managers.IVCellTypeManager()

    SEX_SYMBOLS = {"m": "♂", "f": "♀", "mf": "♂♀", "na": "N/A", "nr": "not reported"}

    study = models.ForeignKey("study.Study", on_delete=models.CASCADE, related_name="ivcelltypes")
    species = models.CharField(max_length=64)
    strain = models.CharField(max_length=64, default="not applicable")
    sex = models.CharField(max_length=2, choices=constants.Sex)
    cell_type = models.CharField(max_length=64)
    culture_type = models.CharField(max_length=2, choices=constants.CultureType)
    tissue = models.CharField(max_length=64)
    source = models.CharField(max_length=128, verbose_name="Source of cell cultures")

    BREADCRUMB_PARENT = "study"

    def __str__(self):
        return f"{self.cell_type} {self.species} {self.tissue}"

    def get_absolute_url(self):
        return reverse("invitro:celltype_detail", args=(self.id,))

    def get_update_url(self):
        return reverse("invitro:celltype_update", args=(self.id,))

    def get_delete_url(self):
        return reverse("invitro:celltype_delete", args=(self.id,))

    def get_sex_symbol(self):
        return self.SEX_SYMBOLS.get(self.sex)

    def get_assessment(self):
        return self.study.assessment

    def get_study(self):
        return self.study


class IVExperiment(models.Model):
    objects = managers.IVExperimentManager()

    study = models.ForeignKey("study.Study", on_delete=models.CASCADE, related_name="ivexperiments")
    name = models.CharField(max_length=128)
    cell_type = models.ForeignKey(
        IVCellType, on_delete=models.CASCADE, related_name="ivexperiments"
    )
    transfection = models.CharField(
        max_length=256,
        help_text="Details on transfection methodology and details on genes or "
        'other genetic material introduced into assay, or "not-applicable"',
    )
    cell_notes = models.TextField(
        blank=True,
        help_text="Description of type of cell-line used (ex: "
        "primary cell-line, immortalized cell-line, stably transfected "
        "cell-line, transient transfected cell-line, etc.)",
    )
    dosing_notes = models.TextField(
        blank=True,
        help_text="Notes describing dosing-protocol, including duration-details",
    )
    metabolic_activation = models.CharField(
        max_length=2,
        choices=constants.MetabolicActivation,
        default=constants.MetabolicActivation.NR,
        help_text="Was metabolic-activation used in system (ex: S9)?",
    )
    serum = models.CharField(
        max_length=128, help_text="Percent serum, serum-type, and/or description"
    )
    has_naive_control = models.BooleanField(default=False)
    has_positive_control = models.BooleanField(default=False)
    positive_control = models.CharField(
        max_length=128, blank=True, help_text="Positive control chemical or other notes"
    )
    has_negative_control = models.BooleanField(default=False)
    negative_control = models.CharField(
        max_length=128, blank=True, help_text="Negative control chemical or other notes"
    )
    has_vehicle_control = models.BooleanField(default=False)
    vehicle_control = models.CharField(
        max_length=128, blank=True, help_text="Vehicle control chemical or other notes"
    )
    control_notes = models.CharField(
        max_length=256, blank=True, help_text="Additional details related to controls"
    )
    dose_units = models.ForeignKey(
        "assessment.DoseUnits", on_delete=models.CASCADE, related_name="ivexperiments"
    )

    BREADCRUMB_PARENT = "study"

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.study.assessment

    def get_absolute_url(self):
        return reverse("invitro:experiment_detail", args=(self.id,))

    def get_update_url(self):
        return reverse("invitro:experiment_update", args=(self.id,))

    def get_delete_url(self):
        return reverse("invitro:experiment_delete", args=(self.id,))

    def get_endpoint_create_url(self):
        return reverse("invitro:endpoint_create", args=(self.id,))

    def get_study(self):
        return self.study


class IVEndpointCategory(AssessmentRootedTagTree):
    cache_template_taglist = "invitro.ivendpointcategory.taglist.assessment-{0}"
    cache_template_tagtree = "invitro.ivendpointcategory.tagtree.assessment-{0}"

    def __str__(self):
        return self.name

    def get_list_representation(self):
        lst = list(self.get_ancestors().values_list("name", flat=True))
        lst.pop(0)
        lst.append(self.name)
        return lst

    @property
    def choice_label(self):
        return ". " * (self.depth - 2) + self.name

    def get_choice_representation(self):
        return (self.id, self.choice_label)

    @classmethod
    def get_choices(cls, assessment_id):
        return [cat.get_choice_representation() for cat in cls.get_assessment_qs(assessment_id)]


class IVEndpoint(BaseEndpoint):
    objects = managers.IVEndpointManager()

    TEXT_CLEANUP_FIELDS = (
        "name",
        "short_description",
        "assay_type",
        "effect",
        "observation_time",
    )

    experiment = models.ForeignKey(IVExperiment, on_delete=models.CASCADE, related_name="endpoints")
    chemical = models.ForeignKey(IVChemical, on_delete=models.CASCADE, related_name="endpoints")
    category = models.ForeignKey(
        IVEndpointCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="endpoints",
    )
    assay_type = models.CharField(max_length=128)
    short_description = models.CharField(
        max_length=128,
        help_text="Short (<128 character) description of effect & measurement",
    )
    effect = models.CharField(max_length=128, help_text="Effect, using common-vocabulary")
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
        "(ex: Figure 1, Table 2, etc.)",
    )
    data_type = models.CharField(
        max_length=2,
        choices=constants.DataType,
        default=constants.DataType.CONTINUOUS,
        verbose_name="Dataset type",
    )
    variance_type = models.PositiveSmallIntegerField(
        default=constants.VarianceType.NA, choices=constants.VarianceType
    )
    response_units = models.CharField(max_length=64, blank=True, verbose_name="Response units")
    values_estimated = models.BooleanField(
        default=False,
        help_text="Response values were estimated using a digital ruler or other methods",
    )
    observation_time = models.CharField(blank=True, max_length=32)
    observation_time_units = models.PositiveSmallIntegerField(
        default=constants.ObservationTimeUnits.NR, choices=constants.ObservationTimeUnits
    )
    NOEL = models.SmallIntegerField(
        verbose_name="NOEL", default=-999, help_text="No observed effect level"
    )
    LOEL = models.SmallIntegerField(
        verbose_name="LOEL", default=-999, help_text="Lowest observed effect level"
    )
    monotonicity = models.PositiveSmallIntegerField(
        default=constants.Monotonicity.NR, choices=constants.Monotonicity
    )
    overall_pattern = models.PositiveSmallIntegerField(
        default=constants.OverallPattern.NA, choices=constants.OverallPattern
    )
    statistical_test_notes = models.CharField(
        max_length=256,
        blank=True,
        help_text="Notes describing details on the statistical tests performed",
    )
    trend_test = models.PositiveSmallIntegerField(
        default=constants.TrendTestResult.NR, choices=constants.TrendTestResult
    )
    trend_test_notes = models.CharField(
        max_length=256,
        blank=True,
        help_text="Notes describing details on the trend-test performed",
    )
    endpoint_notes = models.TextField(
        blank=True, help_text="Any additional notes regarding the endpoint itself"
    )
    result_notes = models.TextField(blank=True, help_text="Qualitative description of the results")
    additional_fields = models.TextField(default="{}")

    BREADCRUMB_PARENT = "experiment"

    class Meta:
        ordering = ("id",)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def get_absolute_url(self):
        return reverse("invitro:endpoint_detail", args=(self.id,))

    def get_update_url(self):
        return reverse("invitro:endpoint_update", args=(self.id,))

    def get_delete_url(self):
        return reverse("invitro:endpoint_delete", args=(self.id,))

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @staticmethod
    def max_dose_count(queryset):
        max_val = 0
        qs = queryset.annotate(max_egs=models.Count("groups")).values_list("max_egs", flat=True)
        if len(qs) > 0:
            max_val = max(qs)
        return max_val

    @staticmethod
    def max_benchmark_count(queryset):
        max_val = 0
        qs = queryset.annotate(max_benchmarks=models.Count("benchmarks")).values_list(
            "max_benchmarks", flat=True
        )
        if len(qs) > 0:
            max_val = max(qs)
        return max_val


class IVEndpointGroup(ConfidenceIntervalsMixin, models.Model):
    objects = managers.IVEndpointGroupManager()

    DIFFERENCE_CONTROL_SYMBOLS = {
        "nc": "↔",
        "-": "↓",
        "+": "↑",
        "nt": "NT",
    }

    endpoint = models.ForeignKey(IVEndpoint, on_delete=models.CASCADE, related_name="groups")
    dose_group_id = models.PositiveSmallIntegerField()
    dose = models.FloatField(validators=[MinValueValidator(0)])
    n = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    response = models.FloatField(blank=True, null=True)
    variance = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    difference_control = models.CharField(
        max_length=2,
        choices=constants.DifferenceControl,
        default=constants.DifferenceControl.NC,
    )
    significant_control = models.CharField(
        max_length=2, default=constants.Significance.NR, choices=constants.Significance
    )
    cytotoxicity_observed = models.BooleanField(
        default=None,
        choices=constants.OBSERVATION_CHOICES,
        null=True,
        blank=True,
    )
    precipitation_observed = models.BooleanField(
        default=None,
        choices=constants.OBSERVATION_CHOICES,
        null=True,
        blank=True,
    )

    @property
    def difference_control_symbol(self):
        return self.DIFFERENCE_CONTROL_SYMBOLS[self.difference_control]

    class Meta:
        ordering = ("endpoint", "dose_group_id")


class IVBenchmark(models.Model):
    objects = managers.IVBenchmarkManager()

    endpoint = models.ForeignKey(IVEndpoint, on_delete=models.CASCADE, related_name="benchmarks")
    benchmark = models.CharField(max_length=32)
    value = models.FloatField()


reversion.register(IVChemical)
reversion.register(IVCellType)
reversion.register(IVExperiment)
reversion.register(IVEndpoint)
reversion.register(IVEndpointGroup)
reversion.register(IVBenchmark)
