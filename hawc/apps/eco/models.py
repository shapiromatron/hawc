from django.db import models
from django.db.models import Q

from ..epi.models import Country
from ..study.models import Study


class State(models.Model):

    code = models.CharField(blank=True, max_length=2)
    name = models.CharField(blank=True, unique=True, max_length=64)

    def __str__(self):

        return self.name

    class Meta:
        verbose_name = "State"


class Climate(models.Model):

    name = models.CharField(max_length=100, blank=True)

    def __str__(self):

        return self.name

    class Meta:
        verbose_name = "Climate"


class Ecoregion(models.Model):

    name = models.CharField(verbose_name="Ecoregion", max_length=100, blank=True,)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ecoregion"


class Vocab(models.Model):
    class Categories(models.IntegerChoices):
        TYPE = 0, "Study type"
        SETTING = 1, "Study setting"
        HABITAT = 2, "Habitat"
        CAUSETERM = 3, "Cause term"
        CAUSEMEASURE = 4, "Cause measure"
        BIOORG = 5, "Biological organization"
        EFFECTTERM = 6, "Effect term"
        EFFECTMEASURE = 7, "Effect measure"
        RESPONSEMEASURETYPE = 8, "Response measure type"
        RESPONSEVARIABILITY = 9, "Response variability"
        STATISTICAL = 10, "Statistical significance measure"

    category = models.IntegerField(choices=Categories.choices)
    value = models.CharField(max_length=100, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.parent:
            return self.parent.value + " | " + self.value
        else:
            return self.value

    class Meta:
        verbose_name = "Vocabulary"
        verbose_name_plural = "Vocabulary"


class Metadata(models.Model):

    study_id = models.ForeignKey(Study, on_delete=models.CASCADE)

    study_type = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": 0},
        on_delete=models.CASCADE,
        help_text="Select the type of study",
        related_name="+",
    )

    study_setting = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": 1},
        on_delete=models.CASCADE,
        help_text="Select the setting in which evidence was generated",
        related_name="+",
    )

    country = models.ManyToManyField(Country, help_text="Select one or more countries")

    state = models.ManyToManyField(
        State, blank=True, help_text="Select one or more states, if applicable."
    )

    ecoregion = models.ManyToManyField(
        Ecoregion, blank=True, help_text="Select one or more Level III Ecoregions, if known",
    )

    habitat = models.ForeignKey(
        Vocab,
        verbose_name="Habitat",
        limit_choices_to={"category": 2},
        on_delete=models.CASCADE,
        blank=True,
        help_text="Select the habitat to which the evidence applies",
        related_name="+",
    )

    habitat_as_reported = models.TextField(
        verbose_name="Habitat as reported",
        blank=True,
        help_text="Copy and paste 1-2 sentences from article",
    )

    climate = models.ManyToManyField(
        Climate, blank=True, help_text="Select one or more climates to which the evidence applies",
    )

    climate_as_reported = models.TextField(
        verbose_name="Climate as reported", blank=True, help_text="Copy and paste from article",
    )

    def __str__(self):
        return self.study_id.short_citation

    class Meta:
        verbose_name = "Metadata"
        verbose_name_plural = "Metadata"


class Cause(models.Model):

    study_id = models.ForeignKey(Study, on_delete=models.CASCADE)

    term = models.ForeignKey(
        Vocab, limit_choices_to={"category": 3}, on_delete=models.CASCADE, related_name="+",
    )  # autocomplete

    measure = models.ForeignKey(
        Vocab, limit_choices_to={"category": 4}, on_delete=models.CASCADE, related_name="+",
    )  # autocomplete

    measure_detail = models.TextField(verbose_name="Cause measure detail", blank=True)

    units = models.CharField(
        verbose_name="Cause units",
        max_length=100,
        help_text="Type the unit associated with the cause term",
    )  # autocomplete? # maybe add vocab here?

    bio_org = models.ForeignKey(
        Vocab,
        limit_choices_to={"category": 5},
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

    class Trajectory(models.IntegerChoices):
        INCREASE = 0, "Increase"
        DECREASE = 1, "Decrease"
        CHANGE = 2, "Change"
        OTHER = 3, "Other"

    trajectory = models.IntegerField(
        choices=Trajectory.choices,
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

    def __str__(self):
        return self.study_id.short_citation + " | " + self.term.value

    class Meta:
        verbose_name = "Cause/Treatment"


class Effect(models.Model):

    cause = models.OneToOneField(Cause, on_delete=models.CASCADE)

    term = models.ForeignKey(
        Vocab,
        verbose_name="Effect term",
        limit_choices_to={"category": 6},
        on_delete=models.CASCADE,
        related_name="+",
    )

    measure = models.ForeignKey(
        Vocab,
        verbose_name="Effect measure",
        limit_choices_to={"category": 7},
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
        limit_choices_to={"category": 5},
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

    class Trajectory(models.IntegerChoices):
        INCREASE = 0, "Increase"
        DECREASE = 1, "Decrease"
        CHANGE = 2, "Change"
        NOCHANGE = 3, "No change"
        OTHER = 4, "Other"

    trajectory = models.IntegerField(
        choices=Trajectory.choices,
        verbose_name="Effect trajectory",
        help_text="Select qualitative description of how the effect measure changes in response to the cause trajectory, if applicable",
    )

    comment = models.TextField(
        verbose_name="Effect comment",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )

    as_reported = models.TextField(
        verbose_name="Effect as  reported", help_text="Copy and paste 1-2 sentences from article",
    )

    modifying_factors = models.CharField(
        verbose_name="Modifying factors",
        max_length=100,
        blank=True,
        help_text="Type one or more factors that affect the relationship between the cause and effect",
    )  # autocomplete - choices TBD

    class Sort(models.IntegerChoices):
        TBD = 0, "TBD"

    sort = models.IntegerField(
        choices=Sort.choices,
        verbose_name="Sort quantitative responses",
        help_text="How do you want to sort multiple quantitative responses?",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.cause.study_id.short_citation + " | " + self.term.value

    class Meta:
        verbose_name = "Effect/Response"


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
        limit_choices_to={"category": 9},
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
        limit_choices_to={"category": 10},
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

    def __str__(self):
        if self.measure_type:
            return (
                self.effect.cause.study_id.short_citation
                + " | "
                + self.effect.term.value
                + " | "
                + self.measure_type.value
            )
        else:
            return self.effect.cause.study_id.short_citation + " | " + self.effect.term.value

    class Meta:
        verbose_name = "Quantitative response information"
        verbose_name_plural = "Quantitative response information"
