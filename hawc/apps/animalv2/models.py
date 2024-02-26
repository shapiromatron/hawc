import reversion
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from ..assessment.models import DSSTox, EffectTag
from ..vocab.models import Term
from . import constants, managers


class Experiment(models.Model):
    objects = managers.ExperimentManager()

    study = models.ForeignKey(
        "study.Study", on_delete=models.CASCADE, related_name="v2_experiments"
    )
    name = models.CharField(
        max_length=80,
        verbose_name="Experiment name",
        help_text="""Short-text used to describe the experiment (i.e. 2-Year Cancer Bioassay, 10-Day Oral, 28-Day Inhalation, etc.) using title style (all words capitalized). If study contains more than one chemical, then also include the chemical name (e.g. 28-Day Oral PFBS).""",
    )
    design = models.CharField(
        max_length=2,
        choices=constants.ExperimentDesign.choices,
        help_text="Design of study being performed",
    )
    has_multiple_generations = models.BooleanField(default=False)
    guideline_compliance = models.CharField(
        max_length=128,
        blank=True,
        help_text="""Description of any compliance methods used (i.e. use of EPA OECD, NTP, or other guidelines; conducted under GLP guideline conditions, non-GLP but consistent with guideline study, etc.). This field response should match any description used in study evaluation in the reporting quality domain, e.g., GLP study (OECD guidelines 414 and 412, 1981 versions). If not reported, then use state \"not reported.\"""",
    )
    comments = models.TextField(
        blank=True,
        help_text="Additional comments (eg., description, animal husbandry, etc.)",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("animalv2:experiment_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("animalv2:experiment_update", args=(self.pk,))

    def get_delete_url(self):
        return reverse("animalv2:experiment_delete", args=(self.pk,))

    def get_assessment(self):
        return self.study.get_assessment()

    def get_study(self):
        return self.study

    def get_has_multiple_generations_display(self) -> str:
        return "Yes" if self.has_multiple_generations else "No"

    @property
    def v2_timepoints(self):
        timepoints = []
        for endpoint in self.v2_endpoints.all():
            timepoints.extend(endpoint.v2_timepoints.all())
        return timepoints


class Chemical(models.Model):
    objects = managers.ChemicalManager()

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="v2_chemicals"
    )
    name = models.CharField(
        max_length=80,
        verbose_name="Chemical name",
        help_text="""This field may get displayed in visualizations, so consider using a common acronym, e.g., BPA instead of Bisphenol A""",
    )
    cas = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Chemical identifier (CAS)",
        help_text="""CAS number for chemical-tested. Use N/A if not applicable. If more than one CAS number is applicable, then use a common one here and indicate others in the comment field below.""",
    )
    dtxsid = models.ForeignKey(
        DSSTox,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="DSSTox substance identifier (DTXSID)",
        related_name="v2_chemicals",
        help_text=DSSTox.help_text(),
    )
    source = models.CharField(max_length=128, verbose_name="Source of chemical", blank=True)
    purity = models.CharField(max_length=128, verbose_name="Chemical purity", blank=True)
    vehicle = models.CharField(
        max_length=64,
        verbose_name="Chemical vehicle",
        help_text="""Describe vehicle (use name as described in methods but also add the common name if the vehicle was described in a non-standard way). Enter "not reported" if the vehicle is not described. For inhalation studies, air can be inferred if not explicitly reported. Examples: "corn oil," "filtered air," \"not reported, but assumed clean air.\"""",
        blank=True,
    )
    comments = models.TextField(
        blank=True,
        help_text="Additional comments (eg., description, animal husbandry, etc.)",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self


class AnimalGroup(models.Model):
    objects = managers.AnimalGroupManager()

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="v2_animal_groups"
    )
    name = models.CharField(
        max_length=80,
        verbose_name="Animal group name",
        help_text="""Name should be: sex, common strain name, species (plural) and use Title Style (e.g. Male Sprague Dawley Rat, Female C57BL/6 Mice, Male and Female C57BL/6 Mice). For developmental studies, include the generation before sex in title (e.g., F1 Male Sprague Dawley Rat or P0 Female C57 Mice)""",
    )
    species = models.ForeignKey(
        "assessment.Species", related_name="v2_animal_groups", on_delete=models.CASCADE
    )
    strain = models.ForeignKey(
        "assessment.Strain",
        on_delete=models.CASCADE,
        related_name="v2_animal_groups",
        help_text='When adding a new strain, put the stock in parenthesis, e.g., "Sprague-Dawley (Harlan)."',
    )
    sex = models.CharField(max_length=1, choices=constants.Sex.choices)
    animal_source = models.CharField(
        max_length=128, help_text="Source from where animals were acquired", blank=True
    )
    lifestage_at_exposure = models.CharField(
        blank=True,
        default="",
        max_length=5,
        choices=constants.Lifestage.choices,
        help_text="""Definitions: <strong>Developmental</strong>: Prenatal and perinatal exposure in dams or postnatal exposure in offspring until sexual maturity (~6 weeks in rats and mice). Include studies with pre-mating exposure <em>if the endpoint focus is developmental</em>. <strong>Juvenile</strong>: Exposure between weaned and sexual maturity. <strong>Adult</strong>: Exposure in sexually mature males or females. <strong>Adult (gestation)</strong>: Exposure in dams during pregnancy. <strong>Multi-lifestage</strong>: includes both developmental and adult (i.e., multi-generational studies, exposure that start before sexual maturity and continue to adulthood)""",
    )
    lifestage_at_assessment = models.CharField(
        blank=True,
        default="",
        max_length=5,
        choices=constants.Lifestage.choices,
        help_text="""Definitions: <strong>Developmental</strong>: Prenatal and perinatal exposure in dams or postnatal exposure in offspring until sexual maturity (~6 weeks in rats and mice). Include studies with pre-mating exposure <em>if the endpoint focus is developmental</em>. <strong>Juvenile</strong>: Exposure between weaned and sexual maturity. <strong>Adult</strong>: Exposure in sexually mature males or females. <strong>Adult (gestation)</strong>: Exposure in dams during pregnancy. <strong>Multi-lifestage</strong>: includes both developmental and adult (i.e., multi-generational studies, exposure that start before sexual maturity and continue to adulthood)""",
    )
    generation = models.CharField(
        blank=True, default="", max_length=2, choices=constants.Generation.choices
    )
    parents = models.ManyToManyField("self", related_name="children", symmetrical=False, blank=True)
    husbandry_and_diet = models.TextField(
        help_text="""Copy paste animal husbandry information from materials and methods, use quotation marks around all text directly copy/pasted from paper. Describe diet as presented in the paper (e.g., "soy-protein free 2020X Teklad," "Atromin 1310", "standard rodent chow").""",
        verbose_name="Animal Husbandry and Diet",
        blank=True,
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self


class Treatment(models.Model):
    objects = managers.TreatmentManager()

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="v2_treatments"
    )
    name = models.CharField(
        max_length=80,
        verbose_name="Treatment name",
        help_text="TODO",
    )
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE, related_name="v2_treatments")
    route_of_exposure = models.CharField(
        max_length=2,
        choices=constants.RouteExposure.choices,
        help_text="Primary route of exposure. If multiple primary-exposures, describe in notes-field below",
    )
    exposure_duration = models.FloatField(
        verbose_name="Exposure duration (days)",
        help_text="Length of exposure period (fractions allowed), used for sorting in visualizations. For single-dose or multiple-dose/same day gavage studies, 1.",
        blank=True,
        null=True,
    )
    exposure_duration_description = models.CharField(
        verbose_name="Exposure duration (text)",
        max_length=128,
        blank=True,
        help_text="""Length of time between start of exposure and outcome assessment, in days when &lt;7 (e.g., 5d), weeks when &ge;7 days to 12 weeks (e.g., 1wk, 12wk), or months when &gt;12 weeks (e.g., 15mon). For repeated measures use descriptions such as "1, 2 and 3 wk".  For inhalations studies, also include hours per day and days per week, e.g., "13wk (6h/d, 7d/wk)." This field is commonly used in visualizations, so use abbreviations (h, d, wk, mon, y) and no spaces between numbers to save space. For reproductive and developmental studies, where possible instead include abbreviated age descriptions such as "GD1-10" or "GD2-PND10". For gavage studies, include the number of doses, e.g. "1wk (1dose/d, 5d/wk)" or "2doses" for a single-day experiment.""",
    )
    exposure_outcome_duration = models.FloatField(
        verbose_name="Exposure-outcome duration (days)",
        help_text="""Optional: Numeric length of time between start of exposure and outcome assessment in days. This field may be used to sort studies which is why days are used as a common metric.""",
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    # also clone dose groups assigned to this treatment
    def clone(self):
        associated_dose_groups = DoseGroup.objects.filter(treatment_id=self.id).order_by(
            "dose_group_id"
        )

        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        for dose_group in associated_dose_groups:
            dose_group.id = None
            dose_group.treatment_id = self.id
            dose_group.save()

        return self


class DoseGroup(models.Model):
    objects = managers.DoseGroupManager()

    treatment = models.ForeignKey(
        Treatment, on_delete=models.CASCADE, related_name="v2_dose_groups"
    )
    dose_group_id = models.PositiveSmallIntegerField()
    dose = models.FloatField(validators=[MinValueValidator(0)])
    dose_units = models.ForeignKey(
        "assessment.DoseUnits", on_delete=models.CASCADE, related_name="v2_dose_groups"
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_assessment(self):
        return self.treatment.get_assessment()

    def get_study(self):
        return self.treatment.get_study()


class Endpoint(models.Model):
    objects = managers.EndpointManager()

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="v2_endpoints"
    )
    name = models.CharField(max_length=128, blank=True, help_text="Endpoint/Adverse Outcome")
    name_term = models.ForeignKey(
        Term,
        related_name="v2_endpoint_name_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    system = models.CharField(max_length=128, blank=True, help_text="Relevant biological system")
    system_term = models.ForeignKey(
        Term,
        related_name="v2_endpoint_system_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    organ = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Organ (and tissue)",
        help_text="Relevant organ or tissue",
    )
    organ_term = models.ForeignKey(
        Term,
        related_name="v2_endpoint_organ_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    effect = models.CharField(
        max_length=128, blank=True, help_text="Effect, using common-vocabulary"
    )
    effect_term = models.ForeignKey(
        Term,
        related_name="v2_endpoint_effect_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    effect_subtype = models.CharField(
        max_length=128, blank=True, help_text="Effect subtype, using common-vocabulary"
    )
    effect_subtype_term = models.ForeignKey(
        Term,
        related_name="v2_endpoint_effect_subtype_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    # these next 4 are so-called flexible dropdowns. e.g. anatomical is
    # "left/right/anterior/Posterior/Cranial/Caudal/Lateral/medial" but we want to let
    # ppl type something else. do we want to store these (and add custom ones) in a table?
    # Or just build the UI to show options from a list but also let user type custom ones
    # (in that case just store it as a string)? leave as string for now.
    effect_modifier_timing = models.CharField(max_length=128, blank=True)
    effect_modifier_reference = models.CharField(max_length=128, blank=True)
    effect_modifier_anatomical = models.CharField(max_length=128, blank=True)
    effect_modifier_location = models.CharField(max_length=128, blank=True)
    additional_tags = models.ManyToManyField(EffectTag, blank=True)
    comments = models.TextField(blank=True, help_text="TODO")

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()

    @property
    def resolved_name(self):
        return self.name_term.name if self.name_term else self.name

    @property
    def resolved_system(self):
        return self.system_term.name if self.system_term else self.system

    @property
    def resolved_organ(self):
        return self.organ_term.name if self.organ_term else self.organ

    @property
    def resolved_effect(self):
        return self.effect_term.name if self.effect_term else self.effect

    @property
    def resolved_effect_subtype(self):
        return self.effect_subtype_term.name if self.effect_subtype_term else self.effect_subtype

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self


class ObservationTime(models.Model):
    objects = managers.ObservationTimeManager()

    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE, related_name="v2_timepoints")
    observation_time = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Observation timepoint",
        help_text="""Numeric value of the time an observation was reported; optional, should be recorded if the same effect was measured multiple times.""",
    )
    observation_time_units = models.PositiveSmallIntegerField(
        default=constants.ObservationTimeUnits.NR,
        choices=constants.ObservationTimeUnits.choices,
    )
    observation_time_text = models.CharField(
        max_length=64,
        blank=True,
        help_text='Text for reported observation time (ex: "60-90 PND")',
    )
    comments = models.TextField(blank=True, help_text="TODO")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_assessment(self):
        return self.endpoint.get_assessment()

    def get_study(self):
        return self.endpoint.get_study()

    def clone(self):
        self.id = None
        self.save()
        return self


class DataExtraction(models.Model):
    objects = managers.DataExtractionManager()

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="v2_data_extractions"
    )
    endpoint = models.ForeignKey(
        Endpoint, on_delete=models.CASCADE, related_name="v2_data_extractions"
    )
    observation_timepoint = models.ForeignKey(
        ObservationTime, on_delete=models.CASCADE, related_name="v2_data_extractions"
    )

    # specific fields
    is_qualitative_only = models.BooleanField(default=False)
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="""Details on where the data are found in the literature (ex: "Figure 1", "Table 2", "Text, p. 24", "Figure 1 and Text, p.24")""",
    )
    variance_type = models.PositiveSmallIntegerField(
        default=constants.VarianceType.SD, choices=constants.VarianceType.choices
    )
    statistical_method = models.CharField(max_length=128, blank=True, help_text="TODO")
    method_to_control_for_litter_effects = models.PositiveSmallIntegerField(
        choices=constants.MethodToControlForLitterEffects.choices
    )
    values_estimated = models.BooleanField(
        default=False,
        help_text="Response values were estimated using a digital ruler or other methods",
    )
    dataset_type = models.CharField(
        blank=True, default="", max_length=2, choices=constants.DatasetType.choices
    )
    statistical_power = models.CharField(max_length=128, blank=True, help_text="TODO")
    response_units = models.CharField(
        max_length=32,
        blank=True,
        help_text="Units the response was measured in (i.e., \u03BCg/dL, % control, etc.)",
    )
    dose_response_observations = models.TextField(help_text="TODO")
    result_details = models.TextField(help_text="TODO")

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_study(self):
        return self.experiment.get_study()


class DoseResponseGroupLevelData(models.Model):
    objects = managers.DoseResponseGroupLevelDataManager()

    data_extraction = models.ForeignKey(
        DataExtraction, on_delete=models.CASCADE, related_name="v2_group_level_data"
    )
    treatment_name = models.CharField(max_length=256, help_text="TODO")
    dose = models.CharField(max_length=128, help_text="TODO")
    # as per guidance, intentionally making this text, not numeric, in case extractors want to note units.
    # could split into separate dose/dose_units instead if desired? See also DoseResponseAnimalLevelData.dose

    n = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    response = models.FloatField()
    variance = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    treatment_related_effect = models.PositiveSmallIntegerField(
        choices=constants.TreatmentRelatedEffect.choices
    )
    statistically_significant = models.PositiveSmallIntegerField(
        choices=constants.StatisticallySignificant.choices
    )
    p_value = models.CharField(max_length=128, blank=True, help_text="TODO")
    NOEL = models.SmallIntegerField(default=-999, help_text="No observed effect level")
    LOEL = models.SmallIntegerField(default=-999, help_text="Lowest observed effect level")

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_assessment(self):
        return self.data_extraction.get_assessment()

    def get_study(self):
        return self.data_extraction.get_study()


class DoseResponseAnimalLevelData(models.Model):
    objects = managers.DoseResponseAnimalLevelDataManager()

    data_extraction = models.ForeignKey(
        DataExtraction, on_delete=models.CASCADE, related_name="v2_animal_level_data"
    )
    cage_id = models.CharField(max_length=128, blank=True, help_text="TODO")
    animal_id = models.CharField(max_length=128, blank=True, help_text="TODO")
    dose = models.CharField(max_length=128, help_text="TODO")
    response = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def get_assessment(self):
        return self.data_extraction.get_assessment()

    def get_study(self):
        return self.data_extraction.get_study()


reversion.register(Experiment)
reversion.register(Chemical)
reversion.register(AnimalGroup)
reversion.register(Treatment)
reversion.register(DoseGroup)
reversion.register(Endpoint)
reversion.register(ObservationTime)
reversion.register(DataExtraction)
reversion.register(DoseResponseGroupLevelData)
reversion.register(DoseResponseAnimalLevelData)
