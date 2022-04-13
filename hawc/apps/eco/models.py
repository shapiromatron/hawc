from django.db import models
from django.db.models import Q
from taggit.managers import TaggableManager

from ..epi.models import Country
from ..study.models import Study
from .constants import ChangeTrajectory, VocabCategories


class State(models.Model):
    code = models.CharField(unique=True, max_length=2)
    name = models.CharField(unique=True, max_length=64)

    def __str__(self):
        return self.name


class Vocab(models.Model):
    category = models.IntegerField(choices=VocabCategories.choices)
    value = models.CharField(max_length=100)
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
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
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
    country = models.ManyToManyField(
        Country,
        help_text="Select one or more countries",
        related_name="country",  # is this a good related name?
    )
    state = models.ManyToManyField(
        State, blank=True, help_text="Select one or more states, if applicable."
    )
    ecoregion = models.ManyToManyField(
        Vocab,
        limit_choices_to={"category": VocabCategories.ECOREGION},
        help_text="Select one or more Level III Ecoregions, if known",
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
    climate = models.ManyToManyField(
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

    class Meta:
        verbose_name = "Ecological Design"
        verbose_name_plural = "Ecological Designs"

    def __str__(self):
        return f"{self.study} - ecological design"


class Cause(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    term = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.CAUSE_TERM},
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Add help text - autocomplete field?",
    )
    measure = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.CAUSE_MEASURE},
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Add help text - autocomplete field?",
    )
    measure_detail = models.TextField(verbose_name="Cause measure detail", blank=True)
    units = models.CharField(
        verbose_name="Cause units",
        max_length=100,
        help_text="Type the unit associated with the cause term. autocomplete?",
    )
    bio_org = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.BIO_ORG},
        verbose_name="Level of biological organization",
        help_text="Select the level of biological organization associated with the cause, if applicable",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    species = models.CharField(
        verbose_name="Cause/treatment species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )
    level = models.CharField(
        verbose_name="Cause/treatment level",
        max_length=128,
        help_text="Describe the specific treatment/exposure/dose level or range of levels of the cause measure",
    )
    level_value = models.FloatField(
        verbose_name="Cause/treatment value",
        blank=True,
        null=True,
        help_text="Type the the specific treatment/exposure/dose level (if applicable)",
    )
    level_units = models.CharField(
        verbose_name="Cause/treatment level units",
        max_length=100,
        help_text="Type the units associated with the cause value term",
    )
    duration = models.CharField(
        verbose_name="Cause/treatment duration",
        max_length=100,
        help_text="Describe the duration or range of durations of the treatment/exposure",
    )
    duration_value = models.FloatField(
        verbose_name="Cause/treatment duration value",
        blank=True,
        null=True,
        help_text="Type the numeric value of the specific duration of the treatment/exposure",
    )  # BR suggestion
    duration_units = models.CharField(
        verbose_name="Cause/treatment duration units",
        max_length=100,
        blank=True,
        help_text="Type the unit associated with the cause duration term. Autocomplete.",
    )
    comment = models.TextField(
        verbose_name="Cause/treatment comment",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )
    as_reported = models.TextField(
        verbose_name="Cause/treatment as reported",
        help_text="Copy and paste exact phrase up to 1-2 sentences from article. If not stated in the article, leave blank.",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cause/Treatment"

    def __str__(self):
        return f"{self.study} | {self.term.value}"


class Effect(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    term = models.ForeignKey(
        Vocab,
        verbose_name="Effect term",
        limit_choices_to={"category": VocabCategories.EFFECT_TERM},
        on_delete=models.CASCADE,
        related_name="+",
    )
    measure = models.ForeignKey(
        Vocab,
        verbose_name="Effect measure",
        limit_choices_to={"category": VocabCategories.EFFECT_MEASURE},
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Add help-text. autocomplete?",
    )
    measure_detail = models.CharField(
        verbose_name="Effect measure detail",
        max_length=100,
        blank=True,
        help_text="Add help-text. autocomplete?",
    )
    units = models.CharField(
        verbose_name="Effect units",
        max_length=100,
        help_text="Type the unit associated with the effect term. autocomplete?",
    )
    species = models.CharField(
        verbose_name="Effect species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )
    bio_org = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.BIO_ORG},
        verbose_name="Level of biological organization",
        help_text="Select the level of biological organization associated with the effect, if applicable",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    comment = models.TextField(
        verbose_name="Effect comment",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )
    as_reported = models.TextField(
        verbose_name="Effect as reported",
        help_text="Copy and paste exact phrase up to 1-2 sentences from article. If not stated in the article, leave blank.",
    )
    modifying_factors = TaggableManager(
        verbose_name="Modifying factors",
        help_text="Type a comma-separated list of any modifying factors, confounding variables, model co-variates, etc. that were analyzed and tested for the potential to influence the relationship between cause and effect",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Effect/Response"

    def __str__(self):
        return f"{self.study} | {self.term.value}"


class Result(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE)
    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)
    sort_order = models.PositiveSmallIntegerField(
        verbose_name="Sort order",
        help_text="Sort order of a multiple responses",
        default=0,
    )
    relationship_direction = models.IntegerField(
        choices=ChangeTrajectory.choices,
        verbose_name="Direction of relationship",
        help_text="Select the direction of the relationship between selected cause and effect",
    )
    relationship_comment = models.TextField(
        verbose_name="Relationship comment",
        blank=True,
        help_text="Describe the relationship in 1-2 sentences",
    )
    modifying_factors_comment = models.TextField(
        verbose_name="Modifying factors comment",
        max_length=256,
        blank=True,
        help_text="Describe how the important modifying factor(s) affect the relationship in 1-2 sentences. Consider factors associated with the study that have an important influence on the relationship between cause and effect. For example, statistical significance of a co-variate in a model can indicate importance.",
    )
    sample_size = models.IntegerField(
        verbose_name="Sample size",
        blank=True,
        help_text="Type the number of samples used to calculate the response measure value, if known",
        null=True,
    )
    measure_type = models.ForeignKey(
        Vocab,
        verbose_name="Response measure type",
        limit_choices_to=(Q(category=8) & Q(parent__isnull=False)),
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Select one response measure type",
    )
    measure_value = models.FloatField(
        verbose_name="Response measure value",
        help_text="Numerical value of the response measure",
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="Response measure description",
        blank=True,
        help_text="Describe any other useful information about the response measure not captured in other fields",
    )
    variability = models.ForeignKey(
        Vocab,
        verbose_name="Response variability",
        limit_choices_to={"category": VocabCategories.RESPONSE_VARIABILITY},
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Select how variability in the response measure was reported, if applicable",
    )
    low_variability = models.FloatField(
        verbose_name="Lower response variability measure",
        blank=True,
        help_text="Type the lower numerical bound of the response variability",
        null=True,
    )
    upper_variability = models.FloatField(
        verbose_name="Upper response variability measure",
        blank=True,
        help_text="Type the upper numerical bound of the response variability",
        null=True,
    )
    statistical_sig_type = models.ForeignKey(
        Vocab,
        verbose_name="Statistical significance measure type",
        limit_choices_to={"category": VocabCategories.STATISTICAL},
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Select the type of statistical significance measure reported",
    )
    statistical_sig_value = models.FloatField(
        verbose_name="Statistical significance measure value",
        blank=True,
        help_text="Type the numerical value of the statistical significance",
        null=True,
    )
    derived_value = models.FloatField(
        verbose_name="Derived response measure value",
        blank=True,
        help_text="Calculation from 'response measure value' based on a formula linked to 'response measure type', if applicable",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"
        unique_together = (("effect", "sort_order"),)
        ordering = ("effect", "sort_order")

    def __str__(self):
        if self.measure_type:
            return f"{self.study} | {self.cause.term.value} |{self.effect.term.value} | {self.measure_type.value}"
        else:
            return f"{self.study} | {self.cause.term.value} | {self.effect.term.value}"

    def default_related(self):
        return {
            "variability": Vocab.objects.get(
                category=VocabCategories.RESPONSE_VARIABILITY, value="Not applicable"
            ),
            "statistical_sig_type": Vocab.objects.get(
                category=VocabCategories.STATISTICAL, value="Not applicable"
            ),
        }
