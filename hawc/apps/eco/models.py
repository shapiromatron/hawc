from django.db import models
from django.db.models import Q

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


class Metadata(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="eco_metadata")

    study_type = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.TYPE},
        on_delete=models.CASCADE,
        help_text="Select the type of study",
        related_name="+",
    )
    study_setting = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.SETTING},
        on_delete=models.CASCADE,
        help_text="Select the setting in which evidence was generated",
        related_name="+",
    )
    country = models.ManyToManyField(Country, help_text="Select one or more countries")
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
        help_text="Copy and paste 1-2 sentences from article",
    )
    climate = models.ManyToManyField(
        Vocab,
        limit_choices_to={"category": VocabCategories.CLIMATE},
        help_text="Select one or more climates to which the evidence applies",
        related_name="+",
    )
    climate_as_reported = models.TextField(
        verbose_name="Climate as reported", blank=True, help_text="Copy and paste from article",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ecological metadata"
        verbose_name_plural = "Ecological metadata"

    def __str__(self):
        return f"{self.study} - ecological metadata"


class Cause(models.Model):

    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    term = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.CAUSE_TERM},
        on_delete=models.CASCADE,
        related_name="+",
    )  # autocomplete
    measure = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": VocabCategories.CAUSE_MEASURE},
        on_delete=models.CASCADE,
        related_name="+",
    )  # autocomplete
    measure_detail = models.TextField(verbose_name="Cause measure detail", blank=True)
    units = models.CharField(
        verbose_name="Cause units",
        max_length=100,
        help_text="Type the unit associated with the cause term",
    )  # autocomplete? # maybe add vocab here?
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
        verbose_name="Cause species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )
    trajectory = models.IntegerField(
        choices=ChangeTrajectory.choices,
        verbose_name="Cause trajectory",
        help_text="Select qualitative description of how the cause measure changes, if applicable",
    )
    comment = models.TextField(
        verbose_name="Cause comment",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )
    as_reported = models.TextField(
        verbose_name="Cause as reported", help_text="Copy and paste 1-2 sentences from article",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cause/Treatment"

    def __str__(self):
        return f"{self.study} | {self.term.value}"


class Effect(models.Model):
    cause = models.OneToOneField(Cause, on_delete=models.CASCADE)
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
    )  # autocomplete
    measure_detail = models.CharField(
        verbose_name="Effect measure detail", max_length=100, blank=True
    )  # autocomplete
    units = models.CharField(
        verbose_name="Effect units",
        max_length=100,
        help_text="Type the unit associated with the effect term",
    )  # autocomplete
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
    species = models.CharField(
        verbose_name="Effect species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )
    trajectory = models.IntegerField(
        choices=ChangeTrajectory.choices,
        verbose_name="Effect trajectory",
        help_text="Select qualitative description of how the effect measure changes in response to the cause trajectory, if applicable",
    )
    comment = models.TextField(
        verbose_name="Effect comment",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )
    as_reported = models.TextField(
        verbose_name="Effect as reported", help_text="Copy and paste 1-2 sentences from article",
    )
    modifying_factors = models.CharField(
        verbose_name="Modifying factors",
        max_length=256,
        blank=True,
        help_text="Comma-separated list of one or more factors that affect the relationship between the cause and effect",
    )  # autocomplete - choices TBD
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Effect/Response"

    def __str__(self):
        return f"{self.cause.study} | {self.term.value}"


class Quantitative(models.Model):
    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)
    cause_level = models.CharField(
        verbose_name="Cause treatment level",
        max_length=100,
        blank=True,
        help_text="Type the specific treatment/exposure/dose level of the cause measure",
    )
    cause_level_value = models.FloatField(
        verbose_name="Cause treatment level value",
        blank=True,
        help_text="Type the numeric value of the specific treatment/exposure/dose level of the cause measure",
        null=True,
    )
    cause_level_units = models.CharField(
        verbose_name="Cause treatment level units",
        max_length=100,
        blank=True,
        help_text="Enter the units of the specific treatment/exposure/dose level of the cause measure",
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
        blank=True,
        null=True,
        help_text="Select one response measure type",
    )
    measure_value = models.FloatField(
        verbose_name="Response measure value",
        blank=True,
        help_text="Type the numerical value of the response measure",
        null=True,
    )
    description = models.TextField(
        verbose_name="Response measure description",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )
    variability = models.ForeignKey(
        Vocab,
        verbose_name="Response variability",
        blank=True,
        null=True,
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
        blank=True,
        null=True,
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
        verbose_name = "Quantitative response information"
        verbose_name_plural = "Quantitative response information"

    def __str__(self):
        if self.measure_type:
            return f"{self.effect.cause.study_id.short_citation} | {self.effect.term.value} | {self.measure_type.value}"
        else:
            return f"{self.effect.cause.study_id.short_citation} | {self.effect.term.value}"
