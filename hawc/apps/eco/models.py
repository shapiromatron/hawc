from django.db import models

study_type_choices = (
    ("Observational/gradient", "Observational/gradient"),
    ("Manipulation/experiment", "Manipulation/experiment"),
    ("Simulation", "Simulation"),
    ("Meta-analysis", "Meta-analysis"),
    ("Review", "Review"),
)
study_setting_choices = (
    ("Field", "Field"),
    ("Mesocosm", "Mesocosm"),
    ("Greenhouse", "Greenhouse"),
    ("Laboratory", "Laboratory"),
    ("Model", "Model"),
    ("Not applicable", "Not applicable"),
)
habitat_choices = (
    ("Terrestrial", "Terrestrial"),
    ("Riparian", "Riparian"),
    ("Freshwater aquatic", "Freshwater aquatic"),
    ("Estuarine", "Estuarine"),
    ("Marine", "Marine"),
)
habitat_terrestrial_choices = (
    ("Forest", "Forest"),
    ("Grassland", "Grassland"),
    ("Desert", "Desert"),
    ("Heathland", "Heathland"),
    ("Agricultural", "Agricultural"),
    ("Urban/suburban", "Urban/suburban"),
    ("Tundra", "Tundra"),
)
habitat_aquatic_freshwater_choices = (
    ("Stream/river", "Stream/river"),
    ("Wetland", "Wetland"),
    ("Lake/reservoir", "Lake/reservoir"),
    ("Artificial", "Artificial"),
)
cause_term_choices = (("TBD", "TBD"), ("Water quality", "Water quality"))
cause_measure_choices = (("TBD", "TBD"), ("Nutrients", "Nutrients"))
cause_bio_org_choices = (
    ("Ecosystem", "Ecosystem"),
    ("Community", "Community"),
    ("Population", "Population"),
    ("Individual organism", "Individual organism"),
    ("Sub-organismal", "Sub-organismal"),
)
cause_trajectory_choices = (
    ("Increase", "Increase"),
    ("Decrease", "Decrease"),
    ("Change", "Change"),
    ("Other", "Other"),
)
effect_term_choices = (("TBD", "TBD"), ("Algae", "Algae"))
effect_measure_choices = (("TBD", "TBD"), ("Abundance", "Abundance"))
effect_bio_org_choices = (
    ("Ecosystem", "Ecosystem"),
    ("Community", "Community"),
    ("Population", "Population"),
    ("Individual organism", "Individual organism"),
    ("Sub-organismal", "Sub-organismal"),
)
effect_trajectory_choices = (
    ("Increase", "Increase"),
    ("Decrease", "Decrease"),
    ("Change", "Change"),
    ("No change", "No change"),
    ("Other", "Other"),
)
modifying_factors_choices = (("TBD", "TBD"),)
response_measure_type_choices = (
    ("Correlation coefficient", "Correlation coefficient"),
    ("R-squared", "R-squared"),
    ("Mean difference", "Mean difference"),
    ("ANOVA/PERMANOVA", "ANOVA/PERMANOVA"),
    ("Ratio", "Ratio"),
    ("Slope coefficient (beta)", "Slope coefficient (beta)"),
    ("Ordination", "Ordination"),
    ("Threshold", "Threshold"),
)
response_measure_type_correlation_choices = (
    ("Pearson", "Pearson"),
    ("Spearman", "Spearman"),
    ("Not specified", "Not specified"),
)
response_measure_type_rsq_choices = (
    ("Simple linear", "Simple linear"),
    ("Partial", "Partial"),
    ("Multiple", "Multiple"),
    ("Quantile", "Quantile"),
    ("Not specified", "Not specified"),
)
response_measure_type_ratio_choices = (
    ("Response ratio", "Response ratio"),
    ("Odds ratio", "Odds ratio"),
    ("Risk ratio", "Risk ratio"),
    ("Hazard ratio", "Hazard ratio"),
    ("Not specified", "Not specified"),
)
response_measure_type_meandiff_choices = (
    ("Non-standardized", "Non-standardized"),
    ("Standardized", "Standardized"),
    ("Not specified", "Not specified"),
)
response_measure_type_slope_choices = (
    ("Non-transformed data", "Non-transformed data"),
    ("Transformed data", "Transformed data"),
    ("Not specified", "Not specified"),
)
response_measure_type_ord_choices = (
    ("Canonical correspondence analysis (CCA)", "Canonical correspondence analysis (CCA)"),
    ("Principal components analysis (PCA)", "Principal components analysis (PCA)"),
    ("Multiple discriminant analysis (MDA)", "Multiple discriminant analysis (MDA)"),
    ("Non-multidimensional scaling (NMDS)", "Non-multidimensional scaling (NMDS)"),
    ("Factor analysis", "Factor analysis"),
    ("Not specified", "Not specified"),
)
response_measure_type_thresh_choices = (
    ("Regression tree", "Regression tree"),
    ("Random forest", "Random forest"),
    ("Breakpoint (piecewise) regression", "Breakpoint (piecewise) regression"),
    ("Quantile regression", "Quantile regression"),
    ("Cumulative frequency distribution", "Cumulative frequency distribution"),
    ("Gradient forest analysis", "Gradient forest analysis"),
    ("Non-linear curve fitting", "Non-linear curve fitting"),
    ("Ordination", "Ordination"),
    ("TITAN", "TITAN"),
    ("Not specified", "Not specified"),
)
response_variability_choices = (
    ("95% CI", "95% CI"),
    ("90% CI", "90% CI"),
    ("Standard deviation", "Standard deviation"),
    ("Standard error", "Standard error"),
    ("Not applicable", "Not applicable"),
)
statistical_sig_measure_type_choices = (
    ("P-value", "P-value"),
    ("F statistic", "F statistic"),
    ("Chi square", "Chi square"),
    ("Not applicable", "Not applicable"),
)
sort_choices = (("TBD", "TBD"),)


class Country(models.Model):

    code = models.CharField(blank=True, max_length=2)
    name = models.CharField(unique=True, max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ("name",)


class State(models.Model):

    code = models.CharField(blank=True, max_length=2)
    name = models.CharField(blank=True, unique=True, max_length=64)

    def __str__(self):

        return self.name

    class Meta:
        verbose_name = "State"


class Climate(models.Model):

    name = models.CharField(max_length=100, blank=True,)

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

    study_id = models.OneToOneField(Reference, on_delete=models.CASCADE)

    study_type = models.CharField(
        max_length=100, choices=study_type_choices, help_text="Select the type of study"
    )

    study_setting = models.CharField(
        max_length=100,
        choices=study_setting_choices,
        help_text="Select the setting in which evidence was generated",
    )

    country = models.ManyToManyField(Country, help_text="Select one or more countries")

    state = models.ManyToManyField(
        State, blank=True, help_text="Select one or more states, if applicable."
    )

    ecoregion = models.ManyToManyField(
        Ecoregion, blank=True, help_text="Select one or more Level III Ecoregions, if known",
    )

    habitat = models.CharField(
        verbose_name="Habitat",
        max_length=100,
        choices=habitat_choices,
        blank=True,
        help_text="Select the habitat to which the evidence applies",
    )

    habitat_terrestrial = models.CharField(
        verbose_name="Terrestrial habitat",
        max_length=100,
        choices=habitat_terrestrial_choices,
        blank=True,
        help_text="If you selected terrestrial, pick the type of terrestrial habitat",
    )  # this field is dependent on selecting terrestrial habitat

    habitat_aquatic_freshwater = models.CharField(
        verbose_name="Freshwater habitat",
        max_length=100,
        choices=habitat_aquatic_freshwater_choices,
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


class Cause(models.Model):

    study_id = models.ForeignKey(Reference, on_delete=models.CASCADE)

    term = models.CharField(
        verbose_name="Cause term", max_length=100, choices=cause_term_choices
    )  # autocomplete

    measure = models.CharField(
        verbose_name="Cause measure", max_length=100, choices=cause_measure_choices
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
        choices=cause_bio_org_choices,
    )

    species = models.CharField(
        verbose_name="Cause species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )

    trajectory = models.CharField(
        verbose_name="Cause trajectory",
        max_length=100,
        choices=cause_trajectory_choices,
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

    term = models.CharField(verbose_name="Effect term", max_length=100, choices=effect_term_choices)

    measure = models.CharField(
        verbose_name="Effect measure", max_length=100, choices=effect_measure_choices
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
        choices=effect_bio_org_choices,
    )

    species = models.CharField(
        verbose_name="Effect species",
        max_length=100,
        blank=True,
        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
    )

    trajectory = models.CharField(
        verbose_name="Effect trajectory",
        max_length=100,
        choices=effect_trajectory_choices,
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
    )  # autocomplete

    sort = models.CharField(
        verbose_name="Sort quantitative responses",
        max_length=100,
        choices=sort_choices,
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

    measure_type_filter = models.CharField(
        verbose_name="Response measure type (filter)",
        max_length=100,
        blank=True,
        choices=response_measure_type_choices,
        help_text="This drop down will filter the following field",
    )

    measure_type = models.CharField(
        verbose_name="Response measure type",
        max_length=40,
        choices=response_measure_type_correlation_choices
        + response_measure_type_rsq_choices
        + response_measure_type_ratio_choices
        + response_measure_type_meandiff_choices
        + response_measure_type_slope_choices
        + response_measure_type_ord_choices
        + response_measure_type_thresh_choices,
        blank=True,
        help_text="Select one response measure type",
    )  # dependent on selection in response measure type column

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

    variability = models.CharField(
        verbose_name="Response variability",
        blank=True,
        max_length=100,
        choices=response_variability_choices,
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

    statistical_sig_type = models.CharField(
        verbose_name="Statistical significance measure type",
        blank=True,
        max_length=100,
        choices=statistical_sig_measure_type_choices,
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
