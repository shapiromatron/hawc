import reversion
from django.db import models
from django.db.models import Q
from django.urls import reverse
from treebeard.mp_tree import MP_Node

from ..common.helper import new_window_a
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
        return "- " * (self.depth - 1) + self.name

    def label(self) -> str:
        # expensive - calls `get_ancestors()`` for each item
        path = ""
        for node in self.get_ancestors():
            path += f"{node.name} > "
        path += f"{self.name}"
        return path


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
    name = models.CharField(blank=True, max_length=128)
    design = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.TYPE},
        on_delete=models.CASCADE,
        help_text="Select study design",
        related_name="+",
    )
    study_setting = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.SETTING},
        on_delete=models.CASCADE,
        help_text="Select the setting in which evidence was generated",
        related_name="+",
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
        limit_choices_to={"category": VocabCategories.ECOREGION},
        help_text=f"Select one or more {new_window_a('https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states', 'Level III Ecoregions')}, if known",
        related_name="+",
    )
    habitat = models.ForeignKey(
        Vocab,
        verbose_name="Habitat",
        limit_choices_to={"category": VocabCategories.HABITAT},
        on_delete=models.CASCADE,
        help_text="Select the habitat to which the evidence applies",
        related_name="+",
    )
    habitat_as_reported = models.TextField(
        verbose_name="Habitat as reported",
        blank=True,
        help_text="Copy and paste exact phrase up to 1-2 sentences from article. If not stated in the article, leave blank.",
    )
    climates = models.ManyToManyField(
        Vocab,
        limit_choices_to={"category": VocabCategories.CLIMATE},
        help_text="Select one or more climates to which the evidence applies",
        related_name="+",
    )
    climate_as_reported = models.TextField(
        verbose_name="Climate as reported",
        blank=True,
        help_text="Copy and paste exact phrase up to 1-2 sentences from article. If not stated in the article, leave blank.",
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


class Cause(models.Model):
    objects = managers.CauseManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="eco_causes")
    name = models.CharField(
        blank=True,
        max_length=128,
        help_text="Name to refer to this cause, commonly used in visualizations",
    )
    term = models.ForeignKey(
        NestedTerm,
        related_name="causes",
        on_delete=models.CASCADE,
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
        help_text="Species name, if applicable; using Common name (Latin binomial)",
    )
    level = models.CharField(
        verbose_name="Level",
        max_length=128,
        help_text="Specific treatment/exposure/dose level or range of levels of the cause measure",
    )
    level_value = models.FloatField(
        verbose_name="Level (numeric)",
        blank=True,
        null=True,
        help_text="Numerical treatment/exposure/dose level, if applicable",
    )
    level_units = models.CharField(
        verbose_name="Value units",
        max_length=128,
        help_text="Units associated with the cause, if applicable",
    )
    duration = models.CharField(
        verbose_name="Duration",
        max_length=128,
        help_text="Duration or range of durations of the treatment/exposure",
    )
    duration_value = models.FloatField(
        verbose_name="Duration (numeric)",
        blank=True,
        null=True,
        help_text="Numeric value of duration of the treatment/exposure",
    )
    duration_units = models.CharField(
        verbose_name="Duration units",
        max_length=128,
        blank=True,
        help_text="Units associated with the duration, if applicable",
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


class Effect(models.Model):
    objects = managers.EffectManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="eco_effects")
    name = models.CharField(
        blank=True,
        max_length=128,
        help_text="Name to refer to this effect/response, commonly used in visualizations",
    )
    term = models.ForeignKey(NestedTerm, related_name="effects", on_delete=models.CASCADE)
    biological_organization = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.BIO_ORG},
        verbose_name="Level of biological organization",
        help_text="Level of biological organization associated with the effect/response, if applicable",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    species = models.CharField(
        verbose_name="Species",
        max_length=128,
        blank=True,
        help_text="Species name, if applicable; using Common name (Latin binomial)",
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


class Result(models.Model):
    objects = managers.ResultManager()

    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name="results")
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
    measure_type = models.ForeignKey(
        Vocab,
        verbose_name="Response measure type",
        limit_choices_to=(
            Q(category=VocabCategories.RESPONSE_MEASURETYPE) & Q(parent__isnull=False)
        ),
        on_delete=models.CASCADE,
        related_name="+",
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
        help_text="Number of samples, if known",
        null=True,
    )
    variability = models.ForeignKey(
        Vocab,
        verbose_name="Response variability",
        limit_choices_to={"category": VocabCategories.RESPONSE_VARIABILITY},
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Variability measurement, if applicable",
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
    modifying_factors = models.CharField(
        verbose_name="Modifying factors",
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
    statistical_sig_type = models.ForeignKey(
        Vocab,
        verbose_name="Statistical significance",
        limit_choices_to={"category": VocabCategories.STATISTICAL},
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Statistical significance measure reported",
    )
    statistical_sig_value = models.FloatField(
        verbose_name="Statistical significance measure value",
        blank=True,
        help_text="Numerical value of the statistical significance",
        null=True,
    )
    description = models.TextField(
        verbose_name="Description",
        blank=True,
        help_text="Additional information not previously described",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"
        unique_together = (("effect", "sort_order"),)
        ordering = ("effect", "sort_order")

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


reversion.register(Design)
reversion.register(Cause)
reversion.register(Effect)
reversion.register(Result)
reversion.register(NestedTerm)
