from django.db import models

from ..epi.models import Country


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


class Reference(models.Model):

    reference = models.CharField(max_length=100, help_text="Enter a Reference ID!")

    def __str__(self):

        return self.reference

    class Meta:
        verbose_name = "Reference"


class Metadata(models.Model):

    study_id = models.ForeignKey(Reference, on_delete=models.CASCADE)

    class StudyType(models.IntegerChoices):

        OBS = 0, "Observational/gradient"
        MAN = 1, "Manipulation/experiment"
        SIM = 2, "Simulation"
        MET = 3, "Meta-analysis"
        REV = 4, "Review"

    study_type = models.CharField(
        max_length=100, choices=StudyType.choices, help_text="Select the type of study"
    )

    class StudySetting(models.IntegerChoices):
        FIELD = 0, "Field"
        MESO = 1, "Mesocosm"
        GREEN = 2, "Greenhouse"
        LAB = 3, "Laboratory"
        MOD = 4, "Model"
        NA = 5, "Not Applicable"

    study_setting = models.CharField(
        max_length=100,
        choices=StudySetting.choices,
        help_text="Select the setting in which evidence was generated",
    )

    country = models.ManyToManyField(Country, help_text="Select one or more countries")

    state = models.ManyToManyField(
        State, blank=True, help_text="Select one or more states, if applicable."
    )

    ecoregion = models.ManyToManyField(
        Ecoregion, blank=True, help_text="Select one or more Level III Ecoregions, if known",
    )

    class HabitatType(models.IntegerChoices):
        TERR = 0, "Terrestrial"
        RIP = 1, "Riparian"
        FRESH = 2, "Freshwater aquatic"
        ESTU = 3, "Estuarine"
        MAR = 4, "Marine"

    habitat = models.CharField(
        verbose_name="Habitat",
        max_length=100,
        choices=HabitatType.choices,
        blank=True,
        help_text="Select the habitat to which the evidence applies",
    )

    class TerrestrialHab(models.IntegerChoices):
        FOR = 0, "Forest"
        GRASS = 1, "Grassland"
        DES = 2, "Desert"
        HEATH = 3, "Heathland"
        AG = 4, "Agricultural"
        URB = 5, "Urban/suburban"
        TUND = 6, "Tundra"

    habitat_terrestrial = models.CharField(
        verbose_name="Terrestrial habitat",
        max_length=100,
        choices=TerrestrialHab.choices,
        blank=True,
        help_text="If you selected terrestrial, pick the type of terrestrial habitat",
    )  # this field is dependent on selecting terrestrial habitat

    class AquaticHab(models.IntegerChoices):
        STREAM = 0, "Stream/river"
        WETL = 1, "Wetland"
        LAKE = 2, "Lake/reservoir"
        ART = 3, "Artificial"

    habitat_aquatic_freshwater = models.CharField(
        verbose_name="Freshwater habitat",
        max_length=100,
        choices=AquaticHab.choices,
        blank=True,
        help_text="If you selected freshwater, pick the type of freshwater habitat",
    )  # this field is dependent on selecting aquatic habitat

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
        return self.study_type

    class Meta:
        verbose_name = "Metadata"


class BioOrg(models.IntegerChoices):  # to be used in both cause and effect tables
    ECOS = 0, "Ecosystem"
    COMM = 1, "Community"
    POP = 2, "Population"
    IND = 3, "Individual organism"
    SUB = 4, "Sub-organismal"


class Cause(models.Model):

    study_id = models.ForeignKey(Reference, on_delete=models.CASCADE)

    class CauseTerm(
        models.IntegerChoices
    ):  # does caroline have an updated list, or does this need to be a fixture??
        TBD = 0, "TBD"
        WAT = 1, "Water Quality"

    term = models.CharField(
        verbose_name="Cause term", max_length=100, choices=CauseTerm.choices
    )  # autocomplete

    class CauseMeasure(
        models.IntegerChoices
    ):  # does caroline have an updated list, or does this need to be a fixture??
        TBD = 0, "TBD"
        NUT = 1, "Nutrients"

    measure = models.CharField(
        verbose_name="Cause measure", max_length=100, choices=CauseMeasure.choices,
    )  # autocomplete

    measure_detail = models.TextField(verbose_name="Cause measure detail", blank=True)

    units = models.CharField(
        verbose_name="Cause units",
        max_length=100,
        help_text="Type the unit associated with the cause term",
    )  # autocomplete?

    bio_org = models.CharField(
        verbose_name="Level of biological organization",
        max_length=100,
        help_text="Select the level of biological organization associated with the cause, if applicable",
        blank=True,
        choices=BioOrg.choices,
    )

    species = models.CharField(
        verbose_name="Cause species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )

    class CauseTrajectory(models.IntegerChoices):
        INCR = 0, "Increase"
        DECR = 1, "Decrease"
        CHANGE = 2, "Change"
        OTHER = 3, "Other"

    trajectory = models.CharField(
        verbose_name="Cause trajectory",
        max_length=100,
        choices=CauseTrajectory.choices,
        help_text="Select qualitative description of how the cause measure changes, if applicable",
    )  # autocomplete

    comment = models.TextField(
        verbose_name="Cause comment",
        blank=True,
        help_text="Type any other useful information not captured in other fields",
    )

    as_reported = models.TextField(
        verbose_name="Cause as reported", help_text="Copy and paste 1-2 sentences from article",
    )

    def __str__(self):
        return self.term

    class Meta:
        verbose_name = "Cause/Treatment"


class Effect(models.Model):

    cause = models.OneToOneField(Cause, on_delete=models.CASCADE)

    class EffectTerm(models.IntegerChoices):  # should this be a fixture?
        TBD = 0, "TBD"
        ALGAE = 1, "Algae"

    term = models.CharField(verbose_name="Effect term", max_length=100, choices=EffectTerm.choices)

    class EffectMeasure(models.IntegerChoices):
        TBD = 0, "TBD"
        ABUND = 1, "Abundance"

    measure = models.CharField(
        verbose_name="Effect measure", max_length=100, choices=EffectMeasure.choices
    )  # autocomplete

    measure_detail = models.CharField(
        verbose_name="Effect measure detail", max_length=100, blank=True
    )  # autocomplete

    units = models.CharField(
        verbose_name="Effect units",
        max_length=100,
        help_text="Type the unit associated with the effect term",
    )  # autocomplete

    bio_org = models.CharField(
        verbose_name="Level of biological organization",
        max_length=100,
        help_text="Select the level of biological organization associated with the cause, if applicable",
        blank=True,
        choices=BioOrg.choices,
    )

    species = models.CharField(
        verbose_name="Effect species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )

    class EffectTrajectory(models.IntegerChoices):
        INCR = 0, "Increase"
        DECR = 1, "Decrease"
        CHANGE = 2, "Change"
        NOCHANGE = 3, "No change"
        OTHER = 4, "Other"

    trajectory = models.CharField(
        verbose_name="Effect trajectory",
        max_length=100,
        choices=EffectTrajectory.choices,
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
        max_length=100,
        help_text="Type one or more factors that affect the relationship between the cause and effect",
    )  # autocomplete - choices TBD

    class Sort(models.IntegerChoices):
        TBD = 0, "TBD"

    sort = models.CharField(
        verbose_name="Sort quantitative responses",
        max_length=100,
        choices=Sort.choices,
        help_text="how do you want to sort multiple quantitative responses?",
        blank=True,
    )

    def __str__(self):
        return self.term

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

    class MeasureTypeFilter(models.IntegerChoices):
        CORR = 0, "Correlation coefficient"
        RSQ = 1, "R-squared"
        MEANDIFF = 2, "Mean difference"
        ANOVA = 3, "ANOVA/PERMANOVA"
        RATIO = 4, "Ratio"
        BETA = 5, "Slope coefficient (beta)"
        ORD = 6, "Ordination"
        THRESH = 7, "Threshold"

    measure_type_filter = models.CharField(
        verbose_name="Response measure type (filter)",
        max_length=100,
        blank=True,
        choices=MeasureTypeFilter.choices,
        help_text="This drop down will filter the following field",
    )  # should this be in the frontend? not 100% sure how to filer one field with another

    class MeasureType(models.IntegerChoices):
        # correlation coefficient:
        PEARSON = 0, "Pearson"
        SPEARMAN = 1, "Spearman"
        # R-squared:
        SIMPLE = 2, "Simple Linear"
        PARTIAL = 3, "Partial"
        MULTIPLE = 4, "Multiple"
        QUANTILE = 5, "Quantile"
        # Ratio:
        RESPONSE = 6, "Response ratio"
        ODDS = 7, "Odds ratio"
        RISK = 8, "Risk ratio"
        HAZARD = 9, "Hazard ratio"
        # Meandiff:
        NONSTAND = 10, "Non-standardized"
        STAND = 11, "Standardized"
        # Slope:
        NONTRANSFORMED = 12, "Non-transformed data"
        TRANSFORMED = 13, "Transformed data"
        # Ordination choices
        CCA = 14, "Canonical correspondence analysis (CCA)"
        PCA = 15, "Principal components analysis (PCA)"
        MDA = 16, "Multiple discriminant analysis (MDA)"
        NMDS = 17, "Non-multidimensional scaling (NMDS)"
        FACTOR = 18, "Factor analysis"
        # Threshold choices
        REGTREE = 19, "Regression tree"
        RANDOMFOREST = 20, "Random forest"
        BREAKPOINT = 21, "Breakpoint (piecewise) regression"
        QUANTREG = 22, "Quantile regression"
        CFD = 23, "Cumulative frequency distribution"
        GFA = 24, "Gradient forest analysis"
        NONLINEAR = 25, "Non-linear curve fitting"
        ORDINATION = 26, "Ordination"
        TITAN = 27, "TITAN"
        # option for each category
        NS = 28, "Not specified"

    measure_type = models.CharField(
        verbose_name="Response measure type",
        max_length=40,
        choices=MeasureType.choices,
        blank=True,
        help_text="Select one response measure type",
    )  # dependent on selection in response measure type filter

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

    class Variability(models.IntegerChoices):
        CI95 = 0, "95% CI"
        CI90 = 1, "90% CI"
        SD = 2, "Standard deviation"
        SE = 3, "Standard error"
        NA = 4, "Not applicable"

    variability = models.CharField(
        verbose_name="Response variability",
        blank=True,
        max_length=100,
        choices=Variability.choices,
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

    class StatisticalSigType(models.IntegerChoices):
        PVAL = 0, "P-value"
        FSTAT = 1, "F statistic"
        CHISQ = 2, "Chi square"
        NA = 3, "Not applicable"

    statistical_sig_type = models.CharField(
        verbose_name="Statistical significance measure type",
        blank=True,
        max_length=100,
        choices=StatisticalSigType.choices,
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

    class Meta:
        verbose_name = "Quantitative response information"
