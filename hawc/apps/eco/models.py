import pandas as pd
import reversion
from django.db import models
from django.db.models import Max, Q
from django.urls import reverse, reverse_lazy
from django.utils.text import format_lazy
from treebeard.mp_tree import MP_Node

from ..common.helper import new_window_a
from ..common.models import NumericTextField
from ..epi.models import Country
from ..study.models import Study
from . import managers
from .constants import ChangeTrajectory, TypeChoices, VocabCategories


class State(models.Model):
    code = models.CharField(unique=True, max_length=2)
    name = models.CharField(unique=True, max_length=64)

    def __str__(self):
        return self.name


class NestedTerm(MP_Node):
    name = models.CharField(max_length=128)
    type = models.CharField(choices=TypeChoices.choices, max_length=2, default="CE")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    node_order_by = ["name"]

    def __str__(self) -> str:
        return self.label()

    @property
    def nested_text(self) -> str:
        return f"{'━ ' * (self.depth - 1)}{self.name}"

    def label(self) -> str:
        # expensive - calls `get_ancestors()`` for each item
        path = ""
        for node in self.get_ancestors():
            path += f"{node.name} > "
        path += f"{self.name}"
        return path

    @classmethod
    def as_dataframe(cls) -> pd.DataFrame:
        max_depth = NestedTerm.objects.aggregate(value=Max("depth"))["value"]
        rows = []
        nesting = [None] * max_depth
        for term in NestedTerm.objects.all():
            depth = term.depth
            nesting[depth - 1] = term.name
            nesting[depth:] = [None] * (max_depth - depth)
            rows.append([term.id, depth, *nesting])

        df = pd.DataFrame(
            data=rows,
            columns=["ID", "Depth", *[f"Level {i+1}" for i in range(len(nesting))]],
        ).fillna("-")

        return df


class Vocab(models.Model):
    category = models.IntegerField(choices=VocabCategories.choices)
    value = models.CharField(max_length=128)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="children",
        related_query_name="children",
    )

    class Meta:
        verbose_name = "Controlled vocabulary"
        verbose_name_plural = "Vocabularies"

    def __str__(self):
        if self.parent:
            return f"{self.parent.value} | {self.value}"
        else:
            return self.value


class Design(models.Model):
    objects = managers.DesignManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="eco_designs")
    name = models.CharField(max_length=128, help_text="Name to refer to this study design")
    design = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.TYPE},
        on_delete=models.CASCADE,
        help_text="Select study design",
        related_name="designs_by_type",
    )
    study_setting = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.SETTING},
        on_delete=models.CASCADE,
        help_text="Select the setting in which evidence was generated",
        related_name="designs_by_setting",
    )
    countries = models.ManyToManyField(
        Country,
        help_text="Select one or more countries",
        related_name="eco_designs",
    )
    states = models.ManyToManyField(
        State, blank=True, help_text="Select one or more states, if applicable."
    )
    ecoregions = models.ManyToManyField(
        Vocab,
        blank=True,
        limit_choices_to={"category": VocabCategories.ECOREGION},
        help_text=f"Select one or more {new_window_a('https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states', 'Level III Ecoregions')}, if known",
        related_name="designs_by_ecoregion",
    )
    habitats = models.ManyToManyField(
        Vocab,
        limit_choices_to={"category": VocabCategories.HABITAT},
        help_text="Select one or more habitats to which the evidence applies.",
        related_name="designs_by_habitat",
    )
    habitats_as_reported = models.TextField(
        verbose_name="Habitats as reported",
        blank=True,
        help_text="Copy and paste exact phrase up to 1-2 sentences from article. If not stated in the article, leave blank.",
    )
    climates = models.ManyToManyField(
        Vocab,
        limit_choices_to={"category": VocabCategories.CLIMATE},
        help_text=f"Select one or more {new_window_a('http://koeppen-geiger.vu-wien.ac.at/present.htm', 'Koppen climate classifications')} to which the evidence applies",
        related_name="designs_by_climate",
    )
    climates_as_reported = models.TextField(
        verbose_name="Climates as reported",
        blank=True,
        help_text="Copy and paste exact phrase up to 1-2 sentences from article. If not stated in the article, leave blank.",
    )
    comments = models.TextField(
        blank=True,
        help_text="Additional information not described in other fields",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study"

    class Meta:
        verbose_name = "Ecological Design"
        verbose_name_plural = "Ecological Designs"

    def __str__(self):
        return self.name

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self

    def get_assessment(self):
        return self.study.get_assessment()

    def get_study(self):
        return self.study

    def get_absolute_url(self):
        return reverse("eco:design_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("eco:design_update", args=(self.pk,))

    def get_delete_url(self):
        return reverse("eco:design_delete", args=(self.pk,))

    @staticmethod
    def flat_complete_header_row():
        return (
            "design-pk",
            "design-url",
            "design-name",
            "design-design_type",
            "design-study_setting",
            "design-countries",
            "design-states",
            "design-ecoregions",
            "design-habitats",
            "design-habitats_as_reported",
            "design-climates",
            "design-climates_as_reported",
            "design-comments",
            "design-created",
            "design-last_updated",
        )

    def flat_complete_data_row(self):
        return (
            self.pk,
            self.get_absolute_url(),
            self.name,
            self.design.value,
            self.study_setting.value,
            "|".join(el.name for el in self.countries.all()),
            "|".join(el.name for el in self.states.all()) if self.states else "",
            "|".join(el.value for el in self.ecoregions.all()) if self.ecoregions else "",
            "|".join(el.value for el in self.habitats.all()) if self.habitats else "",
            self.habitats_as_reported,
            "|".join(el.value for el in self.climates.all()),
            self.climates_as_reported,
            self.comments,
            self.created,
            self.last_updated,
        )


class Cause(models.Model):
    objects = managers.CauseManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="eco_causes")
    name = models.CharField(
        max_length=128,
        help_text="Name to refer to this cause, commonly used in visualizations",
    )
    term = models.ForeignKey(
        NestedTerm,
        related_name="causes",
        on_delete=models.CASCADE,
        help_text=format_lazy(
            "Begin typing or scroll to find the most detailed controlled vocabulary term possible; view entire <a href='{link}'>term list</a>",
            link=reverse_lazy("eco:term_list"),
        ),
    )
    biological_organization = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.BIO_ORG},
        verbose_name="Biological organization",
        help_text="Level of biological organization associated with the cause, if applicable",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    species = models.CharField(
        verbose_name="Species",
        max_length=128,
        blank=True,
        help_text="One or more species names, if applicable; using Common name (Latin binomial)",
    )
    level = models.TextField(
        verbose_name="Level",
        help_text="Describe the treatment/exposure/dose level or range of levels of the cause measure",
    )
    level_value = models.FloatField(
        verbose_name="Level (numeric)",
        blank=True,
        null=True,
        help_text="Specific numeric value of treatment/exposure/dose level, if applicable",
    )
    level_units = models.CharField(
        verbose_name="Level units",
        max_length=128,
        help_text="Units associated with the treatment/exposure/dose level, if applicable",
        blank=True,
    )
    duration = models.CharField(
        verbose_name="Duration",
        max_length=128,
        help_text="Describe the duration or range of durations of the treatment/exposure",
    )
    duration_value = models.FloatField(
        verbose_name="Duration (numeric)",
        blank=True,
        null=True,
        help_text="Specific numeric value of duration of treatment/exposure/dose level, if applicable",
    )
    duration_units = models.CharField(
        verbose_name="Duration units",
        max_length=128,
        blank=True,
        help_text="Units associated with the duration, if applicable",
    )
    exposure = models.CharField(
        verbose_name="Exposure metric",
        max_length=128,
        help_text="Describe any reported exposure metrics (e.g., AOT40, kg/ha/yr)",
        blank=True,
    )
    exposure_value = models.FloatField(
        verbose_name="Exposure metric (numeric)",
        blank=True,
        null=True,
        help_text="Specific numeric value of exposure metric reported, if applicable",
    )
    exposure_units = models.CharField(
        verbose_name="Exposure metric units",
        max_length=128,
        blank=True,
        help_text="Units associated with the exposure metric",
    )
    as_reported = models.TextField(
        verbose_name="Cause (as reported)",
        blank=True,
        help_text="Copy and paste exact phrase up to 1-2 sentences from article. This may be useful for future machine-learning applications.",
    )
    comments = models.TextField(
        verbose_name="Comments",
        blank=True,
        help_text="Additional information not previously described",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cause"

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.study.get_assessment()

    def get_study(self):
        return self.study

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self

    @staticmethod
    def flat_complete_header_row():
        return (
            "cause-pk",
            "cause-name",
            "cause-term",
            "cause-biological-organization",
            "cause-species",
            "cause-level",
            "cause-level_value",
            "cause-level_units",
            "cause-duration",
            "cause-duration_value",
            "cause-duration_units",
            "cause-exposure",
            "cause-exposure_value",
            "cause-exposure_units",
            "cause-as_reported",
            "cause-comments",
            "cause-created",
            "cause-last_updated",
        )

    def flat_complete_data_row(self):
        return (
            self.pk,
            self.name,
            self.term.label(),
            self.biological_organization.value if self.biological_organization else "",
            self.species,
            self.level,
            self.level_value,
            self.level_units,
            self.duration,
            self.duration_value,
            self.duration_units,
            self.exposure,
            self.exposure_value,
            self.exposure_units,
            self.as_reported,
            self.comments,
            self.created,
            self.last_updated,
        )


class Effect(models.Model):
    objects = managers.EffectManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="eco_effects")
    name = models.CharField(
        max_length=128,
        help_text="Name to refer to this effect/response, commonly used in visualizations",
    )
    term = models.ForeignKey(
        NestedTerm,
        related_name="effects",
        on_delete=models.CASCADE,
        help_text=format_lazy(
            "Begin typing or scroll to find the most detailed controlled vocabulary term possible; view entire <a href='{link}'>term list</a>",
            link=reverse_lazy("eco:term_list"),
        ),
    )
    biological_organization = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.BIO_ORG},
        verbose_name="Level of biological organization",
        help_text="Level of biological organization associated with the effect/response, if applicable",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="effect_by_bio",
    )
    species = models.CharField(
        verbose_name="Species",
        max_length=128,
        blank=True,
        help_text="One or more species names, if applicable; using Common name (Latin binomial)",
    )
    units = models.CharField(
        verbose_name="Units",
        max_length=128,
        help_text="Units associated with the effect/response, if applicable",
    )
    as_reported = models.TextField(
        verbose_name="Effect (as reported)",
        blank=True,
        help_text="Copy and paste exact phrase up to 1-2 sentences from article. This may be useful for future machine-learning applications.",
    )
    comments = models.TextField(
        verbose_name="Comments",
        blank=True,
        help_text="Additional information not previously described",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Effect/Response"

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.study.get_assessment()

    def get_study(self):
        return self.study

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self

    @staticmethod
    def flat_complete_header_row():
        return (
            "effect-pk",
            "effect-name",
            "effect-term",
            "effect-biological_organization",
            "effect-species",
            "effect-units",
            "effect-as_reported",
            "effect-comments",
            "effect-created",
            "effect-last_updated",
        )

    def flat_complete_data_row(self):
        return (
            self.pk,
            self.name,
            self.term.label(),
            self.biological_organization.value if self.biological_organization else "",
            self.species,
            self.units,
            self.as_reported,
            self.comments,
            self.created,
            self.last_updated,
        )


class Result(models.Model):
    objects = managers.ResultManager()

    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name="results")
    name = models.CharField(
        max_length=128,
        help_text="Name to refer to this result",
    )
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE)
    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)
    sort_order = models.PositiveSmallIntegerField(
        verbose_name="Sort order",
        help_text="Sort order of multiple responses in visualizations and data tables",
        default=0,
    )
    relationship_direction = models.IntegerField(
        choices=ChangeTrajectory.choices,
        verbose_name="Direction of relationship",
        help_text="Direction of cause and effect relationship",
    )
    relationship_comment = models.TextField(
        verbose_name="Relationship comment",
        blank=True,
        help_text="Describe the relationship in 1-2 sentences",
    )
    statistical_sig_type = models.ForeignKey(
        Vocab,
        verbose_name="Statistical significance",
        limit_choices_to={"category": VocabCategories.STATISTICAL},
        on_delete=models.CASCADE,
        related_name="result_by_sig",
        help_text="Statistical significance measure reported",
    )
    statistical_sig_value = NumericTextField(
        max_length=16,
        blank=True,
        default="",
        verbose_name="Statistical significance value",
        help_text="Numerical value of the statistical significance. Non-numeric values can be used if necessary, but should be limited to <, ≤, ≥, >.",
    )
    modifying_factors = models.CharField(
        verbose_name="Modifying factors",
        blank=True,
        max_length=256,
        default="",
        help_text="A comma-separated list of modifying factors, confounding variables, model co-variates, etc. that were analyzed and tested for the potential to influence the relationship between cause and effect",
    )
    modifying_factors_comment = models.TextField(
        verbose_name="Modifying factors comment",
        max_length=256,
        blank=True,
        help_text="Describe how the important modifying factor(s) affect the relationship in 1-2 sentences. Consider factors associated with the study that have an important influence on the relationship between cause and effect. For example, statistical significance of a co-variate in a model can indicate importance.",
    )
    measure_type = models.ForeignKey(
        Vocab,
        verbose_name="Response measure type",
        limit_choices_to=(
            Q(category=VocabCategories.RESPONSE_MEASURETYPE) & Q(parent__isnull=False)
        ),
        on_delete=models.CASCADE,
        related_name="result_by_measure",
        help_text="Response measure type",
        blank=True,
        null=True,
    )
    measure_value = models.FloatField(
        verbose_name="Response measure",
        help_text="Numerical response as reported",
        blank=True,
        null=True,
    )
    derived_value = models.FloatField(
        verbose_name="Derived response measure",
        blank=True,
        help_text="Calculated from 'response measure' based on a formula in 'response measure type', if applicable",
        null=True,
    )
    sample_size = models.IntegerField(
        verbose_name="Sample size",
        blank=True,
        help_text="Number of samples used to calculate numerical response measure. If you need to report number of control samples and number of treatment samples, use Comment",
        null=True,
    )
    variability = models.ForeignKey(
        Vocab,
        verbose_name="Response variability",
        limit_choices_to={"category": VocabCategories.RESPONSE_VARIABILITY},
        on_delete=models.CASCADE,
        related_name="result_by_variability",
        help_text="Type of variability reported for the numeric response measure",
        null=True,
        blank=True,
    )
    low_variability = models.FloatField(
        verbose_name="Lower response measure",
        blank=True,
        help_text="Lower numerical bound of the response variability",
        null=True,
    )
    upper_variability = models.FloatField(
        verbose_name="Upper response measure",
        blank=True,
        help_text="Upper numerical bound of the response variability",
        null=True,
    )
    comments = models.TextField(
        blank=True,
        help_text="Additional information not previously described",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"
        ordering = ("design", "cause", "effect", "sort_order")

    def __str__(self):
        return f"{self.cause} | {self.effect}"

    def clone(self):
        self.id = None
        self.sort_order = self.sort_order + 1
        self.save()
        return self

    def get_assessment(self):
        return self.design.study.get_assessment()

    def get_study(self):
        return self.design.study

    def default_related(self):
        return {
            "variability": Vocab.objects.get(
                category=VocabCategories.RESPONSE_VARIABILITY, value="Not applicable"
            ),
            "statistical_sig_type": Vocab.objects.get(
                category=VocabCategories.STATISTICAL, value="Not applicable"
            ),
        }

    @staticmethod
    def flat_complete_header_row():
        return (
            "result-pk",
            "result-name",
            "result-cause",
            "result-effect",
            "result-sort_order",
            "result-relationship_direction",
            "result-relationship_comment",
            "result-statistical_sig_type",
            "result-statistical_sig_value",
            "result-modifying_factors",
            "result-modifying_factors_comment",
            "result-measure_type",
            "result-measure_value",
            "result-derived_value",
            "result-sample_size",
            "result-variability",
            "result-low_variability",
            "result-upper_variability",
            "result-comments",
            "result-created",
            "result-last_updated",
        )

    def flat_complete_data_row(self):
        return (
            self.pk,
            self.name,
            self.cause.name,
            self.effect.name,
            self.sort_order,
            self.get_relationship_direction_display(),
            self.relationship_comment,
            self.statistical_sig_type.value,
            self.statistical_sig_value,
            self.modifying_factors,
            self.modifying_factors_comment,
            self.measure_type.value if self.measure_type else "",
            self.measure_value,
            self.derived_value,
            self.sample_size,
            self.variability.value if self.variability else "",
            self.low_variability,
            self.upper_variability,
            self.comments,
            self.created,
            self.last_updated,
        )

    @classmethod
    def complete_df(cls, assessment_id: int) -> pd.DataFrame:
        study_df = Study.objects.filter(assessment_id=assessment_id).flat_df().add_prefix("study-")
        design_df = (
            Design.objects.filter(study__assessment_id=assessment_id)
            .flat_df()
            .add_prefix("design-")
        )
        cause_df = (
            Cause.objects.filter(study__assessment_id=assessment_id).flat_df().add_prefix("cause-")
        )
        effect_df = (
            Effect.objects.filter(study__assessment_id=assessment_id)
            .flat_df()
            .add_prefix("effect-")
        )
        result_df = (
            cls.objects.filter(design__study__assessment_id=assessment_id)
            .flat_df()
            .add_prefix("result-")
        )
        tmp1 = pd.merge(effect_df, result_df, left_on="effect-id", right_on="result-effect_id")
        tmp2 = pd.merge(cause_df, tmp1, left_on="cause-id", right_on="result-cause_id")
        tmp3 = pd.merge(design_df, tmp2, left_on="design-id", right_on="result-design_id")
        return pd.merge(study_df, tmp3, left_on="study-id", right_on="design-study_id")


reversion.register(Design)
reversion.register(Cause)
reversion.register(Effect)
reversion.register(Result)
reversion.register(NestedTerm)
