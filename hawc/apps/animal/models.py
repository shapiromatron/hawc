import collections
import json
import math
from itertools import chain
from typing import Any, Dict

import pandas as pd
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ModelForm
from django.urls import reverse
from reversion import revisions as reversion
from scipy import stats

from ..assessment.models import Assessment, BaseEndpoint, DSSTox
from ..assessment.serializers import AssessmentSerializer
from ..common.helper import (
    HAWCDjangoJSONEncoder,
    SerializerHelper,
    cleanHTML,
    df_move_column,
    tryParseInt,
)
from ..study.models import Study
from ..vocab.models import Term
from . import managers


class Experiment(models.Model):
    objects = managers.ExperimentManager()

    EXPERIMENT_TYPE_CHOICES = (
        ("Ac", "Acute (<24 hr)"),
        ("St", "Short-term (1-30 days)"),
        ("Sb", "Subchronic (30-90 days)"),
        ("Ch", "Chronic (>90 days)"),
        ("Ca", "Cancer"),
        ("Me", "Mechanistic"),
        ("Rp", "Reproductive"),
        ("1r", "1-generation reproductive"),
        ("2r", "2-generation reproductive"),
        ("Dv", "Developmental"),
        ("Ot", "Other"),
        ("NR", "Not-reported"),
    )

    EXPERIMENT_TYPE_DICT = {el[0]: el[1] for el in EXPERIMENT_TYPE_CHOICES}

    PURITY_QUALIFIER_CHOICES = ((">", ">"), ("≥", "≥"), ("=", "="), ("", ""))

    TEXT_CLEANUP_FIELDS = (
        "name",
        "chemical",
        "cas",
        "chemical_source",
        "vehicle",
        "description",
        "guideline_compliance",
    )

    study = models.ForeignKey("study.Study", on_delete=models.CASCADE, related_name="experiments")
    name = models.CharField(
        max_length=80,
        help_text="Short-text used to describe the experiment "
        "(i.e. 2-Year Cancer Bioassay, 10-Day Oral, 28-Day Inhalation, etc.) "
        "using title style (all words capitalized). If study contains more "
        "than one chemical, then also include the chemical name (e.g. 28-Day Oral PFBS).",
    )
    type = models.CharField(
        max_length=2,
        choices=EXPERIMENT_TYPE_CHOICES,
        help_text="Type of study being performed; be as specific as possible",
    )
    has_multiple_generations = models.BooleanField(default=False)
    chemical = models.CharField(
        max_length=128,
        verbose_name="Chemical name",
        blank=True,
        help_text="This field may get displayed in visualizations, "
        "so consider using a common acronym, e.g., BPA instead of Bisphenol A",
    )
    cas = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Chemical identifier (CAS)",
        help_text="""
                CAS number for chemical-tested. Use N/A if not applicable. If more than one
                CAS number is applicable, then use a common one here and indicate others
                in the comment field below.
                """,
    )
    dtxsid = models.ForeignKey(
        DSSTox,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="DSSTox substance identifier (DTXSID)",
        related_name="experiments",
        help_text="""
        <a href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DSSTox</a>
        substance identifier (recommended). When using an identifier, chemical name and CASRN are
        standardized using the DTXSID.
        """,
    )
    chemical_source = models.CharField(
        max_length=128, verbose_name="Source of chemical", blank=True
    )
    purity_available = models.BooleanField(default=True, verbose_name="Chemical purity available?")
    purity_qualifier = models.CharField(
        max_length=1, choices=PURITY_QUALIFIER_CHOICES, blank=True, default=""
    )
    purity = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Chemical purity (%)",
        help_text="Percentage (ex: 95%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    vehicle = models.CharField(
        max_length=64,
        verbose_name="Chemical vehicle",
        help_text="Describe vehicle (use name as described in methods but also add the "
        + "common name if the vehicle was described in a non-standard way). "
        + 'Enter "not reported" if the vehicle is not described. For inhalation '
        + "studies, air can be inferred if not explicitly reported. "
        + 'Examples: "corn oil," "filtered air," "not reported, but assumed clean air."',
        blank=True,
    )
    guideline_compliance = models.CharField(
        max_length=128,
        blank=True,
        help_text="""
            Description of any compliance methods used (i.e. use of EPA OECD, NTP,
            or other guidelines; conducted under GLP guideline conditions, non-GLP but consistent
            with guideline study, etc.). This field response should match any description used
            in study evaluation in the reporting quality domain, e.g., GLP study (OECD guidelines
            414 and 412, 1981 versions). If not reported, then use state "not reported."
            """,
    )
    description = models.TextField(
        blank=True,
        verbose_name="Comments",
        help_text="Add additional comments. In most cases, this field will "
        "be blank. Note that dosing-regime information and animal "
        "details are captured in the Animal Group extraction module.",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = "experiments"
    BREADCRUMB_PARENT = "study"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("animal:experiment_detail", args=(self.pk,))

    def is_generational(self):
        return self.has_multiple_generations

    def get_assessment(self):
        return self.study.get_assessment()

    @staticmethod
    def flat_complete_header_row():
        return (
            "experiment-id",
            "experiment-url",
            "experiment-name",
            "experiment-type",
            "experiment-has_multiple_generations",
            "experiment-chemical",
            "experiment-cas",
            "experiment-dtxsid",
            "experiment-chemical_source",
            "experiment-purity_available",
            "experiment-purity_qualifier",
            "experiment-purity",
            "experiment-vehicle",
            "experiment-guideline_compliance",
            "experiment-description",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["url"],
            ser["name"],
            ser["type"],
            ser["has_multiple_generations"],
            ser["chemical"],
            ser["cas"],
            ser["dtxsid"],
            ser["chemical_source"],
            ser["purity_available"],
            ser["purity_qualifier"],
            ser["purity"],
            ser["vehicle"],
            ser["guideline_compliance"],
            cleanHTML(ser["description"]),
        )

    @classmethod
    def delete_caches(cls, ids):
        Endpoint.delete_caches(
            Endpoint.objects.filter(animal_group__experiment__in=ids).values_list("id", flat=True)
        )

    def copy_across_assessments(self, cw):
        children = list(self.animal_groups.all().order_by("id"))
        old_id = self.id
        self.id = None
        self.study_id = cw[Study.COPY_NAME][self.study_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        cw[AnimalGroup.COPY_NAME]["parents"] = collections.defaultdict(list)
        for child in children:
            child.copy_across_assessments(cw)
        for child in self.animal_groups.all():
            child.complete_copy(cw)

    def get_study(self):
        return self.study


class AnimalGroup(models.Model):
    objects = managers.AnimalGroupManager()

    SEX_SYMBOLS = {"M": "♂", "F": "♀", "C": "♂♀", "R": "NR"}

    SEX_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("C", "Combined"),
        ("R", "Not reported"),
    )

    SEX_DICT = {el[0]: el[1] for el in SEX_CHOICES}

    GENERATION_CHOICES = (
        ("", "N/A (not generational-study)"),
        ("P0", "Parent-generation (P0)"),
        ("F1", "First-generation (F1)"),
        ("F2", "Second-generation (F2)"),
        ("F3", "Third-generation (F3)"),
        ("F4", "Fourth-generation (F4)"),
        ("Ot", "Other"),
    )

    GENERATION_DICT = {el[0]: el[1] for el in GENERATION_CHOICES}

    # these choices for lifesage expose/assessed were added ~Sept 2018. B/c there
    # are existing values in the database, we are not going to enforce these choices on
    # the model as we do for say sex/SEX_CHOICES. Instead we'll leave the model as is,
    # and start using this to drive a Select widget on the form. For old/existing data,
    # we'll add the previously saved value to the dropdown at runtime so we don't lose data.
    LIFESTAGE_CHOICES = (
        ("Developmental", "Developmental"),
        ("Adult", "Adult"),
        ("Adult (gestation)", "Adult (gestation)"),
        ("Multi-lifestage", "Multi-lifestage"),
    )

    TEXT_CLEANUP_FIELDS = (
        "name",
        "animal_source",
        "lifestage_exposed",
        "lifestage_assessed",
        "comments",
        "diet",
    )

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="animal_groups"
    )
    name = models.CharField(
        max_length=80,
        help_text="""
            Name should be: sex, common strain name, species (plural) and use Title Style
            (e.g. Male Sprague Dawley Rat, Female C57BL/6 Mice, Male and Female
            C57BL/6 Mice). For developmental studies, include the generation before
            sex in title (e.g., F1 Male Sprague Dawley Rat or P0 Female C57 Mice)
            """,
    )
    species = models.ForeignKey("assessment.Species", on_delete=models.CASCADE)
    strain = models.ForeignKey(
        "assessment.Strain",
        on_delete=models.CASCADE,
        help_text="When adding a new strain, put the stock in parenthesis, e.g., "
        + '"Sprague-Dawley (Harlan)."',
    )
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    animal_source = models.CharField(
        max_length=128, help_text="Source from where animals were acquired", blank=True
    )
    lifestage_exposed = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Exposure lifestage",
        help_text="Definitions: <strong>Developmental</strong>: Prenatal and perinatal exposure in dams "
        "or postnatal exposure in offspring until sexual maturity (~6 weeks "
        "in rats and mice). Include studies with pre-mating exposure <em>if the "
        "endpoint focus is developmental</em>. <strong>Adult</strong>: Exposure in sexually "
        "mature males or females. <strong>Adult (gestation)</strong>: Exposure in dams during"
        "pregnancy. <strong>Multi-lifestage</strong>: includes both developmental and adult "
        "(i.e., multi-generational studies, exposure that start before sexual "
        "maturity and continue to adulthood)",
    )
    lifestage_assessed = models.CharField(
        max_length=32,
        blank=True,
        help_text="Definitions: <b>Developmental</b>: Prenatal and perinatal exposure in dams or "
        + "postnatal exposure in offspring until sexual maturity (~6 weeks in rats and "
        + "mice). Include studies with pre-mating exposure if the endpoint focus is "
        + "developmental. <b>Adult</b>: Exposure in sexually mature males or females. <b>Adult "
        + "(gestation)</b>: Exposure in dams during pregnancy. <b>Multi-lifestage</b>: includes both "
        + "developmental and adult (i.e., multi-generational studies, exposure that start "
        + "before sexual maturity and continue to adulthood)",
    )
    siblings = models.ForeignKey("self", blank=True, null=True, on_delete=models.SET_NULL)
    generation = models.CharField(blank=True, default="", max_length=2, choices=GENERATION_CHOICES)
    parents = models.ManyToManyField("self", related_name="children", symmetrical=False, blank=True)
    dosing_regime = models.ForeignKey(
        "DosingRegime",
        on_delete=models.SET_NULL,
        help_text="Specify an existing dosing regime or create a new dosing regime below",
        blank=True,
        null=True,
    )  # not enforced in db, but enforced in views
    comments = models.TextField(
        blank=True,
        verbose_name="Animal Source and Husbandry",
        help_text="Copy paste animal husbandry information from materials and methods, "
        "use quotation marks around all text directly copy/pasted from paper.",
    )
    diet = models.TextField(
        help_text='Describe diet as presented in the paper (e.g., "soy-protein free '
        + '2020X Teklad," "Atromin 1310", "standard rodent chow").',
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = "animal_groups"
    BREADCRUMB_PARENT = "experiment"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("animal:animal_group_detail", args=(self.pk,))

    def get_assessment(self):
        return self.experiment.get_assessment()

    @property
    def is_generational(self):
        return self.experiment.is_generational()

    @property
    def sex_symbol(self):
        return self.SEX_SYMBOLS.get(self.sex)

    def get_doses_json(self, json_encode=True):
        if not hasattr(self, "doses"):
            self.doses = [{"error": "no dosing regime"}]
            self.doses = self.dosing_regime.get_doses_json(False)
        if json_encode:
            return json.dumps(self.doses, cls=HAWCDjangoJSONEncoder)
        return self.doses

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @property
    def generation_short(self):
        return self.get_generation_short(self.generation)

    @classmethod
    def get_generation_short(cls, value) -> str:
        return "Other" if value == "Ot" else value

    @staticmethod
    def flat_complete_header_row():
        return (
            "animal_group-id",
            "animal_group-url",
            "animal_group-name",
            "animal_group-sex",
            "animal_group-animal_source",
            "animal_group-lifestage_exposed",
            "animal_group-lifestage_assessed",
            "animal_group-siblings",
            "animal_group-parents",
            "animal_group-generation",
            "animal_group-comments",
            "animal_group-diet",
            "species-name",
            "strain-name",
        )

    @classmethod
    def get_relation_id(cls, rel):
        return str(rel["id"]) if rel else None

    @classmethod
    def flat_complete_data_row(cls, ser):
        return (
            ser["id"],
            ser["url"],
            ser["name"],
            ser["sex"],
            ser["animal_source"],
            ser["lifestage_exposed"],
            ser["lifestage_assessed"],
            cls.get_relation_id(ser["siblings"]),
            "|".join([cls.get_relation_id(p) for p in ser["parents"]]),
            ser["generation"],
            cleanHTML(ser["comments"]),
            ser["diet"],
            ser["species"],
            ser["strain"],
        )

    @classmethod
    def delete_caches(cls, ids):
        Endpoint.delete_caches(
            Endpoint.objects.filter(animal_group__in=ids).values_list("id", flat=True)
        )

    def copy_across_assessments(self, cw, skip_siblings: bool = False):
        children = list(self.endpoints.all().order_by("id"))
        old_id = self.id
        parent_ids = [p.id for p in self.parents.all()]
        self.id = None
        self.experiment_id = cw[Experiment.COPY_NAME][self.experiment_id]
        self.save()

        # set two-way sibling relationship; use skip_siblings to prevent recursion
        if self.siblings and not skip_siblings:
            if self.siblings_id not in cw[self.COPY_NAME]:
                self.siblings.copy_across_assessments(cw, skip_siblings=True)
            self.siblings_id = cw[self.COPY_NAME][self.siblings_id]
            self.__class__.objects.filter(id=self.siblings_id).update(siblings_id=self.id)
            self.save()

        cw[self.COPY_NAME][old_id] = self.id
        cw[self.COPY_NAME]["parents"][self.id] = parent_ids
        for child in children:
            child.copy_across_assessments(cw)

    def complete_copy(self, cw):
        # copy parent animal group over
        for old_parent_id in cw[self.COPY_NAME]["parents"][self.id]:
            parent_id = cw[AnimalGroup.COPY_NAME][old_parent_id]
            self.parents.add(AnimalGroup.objects.get(pk=parent_id))
        # only create dosing_regime if it doesn't exist
        dosing_regime_created = DosingRegime.objects.filter(
            pk=cw[DosingRegime.COPY_NAME].get(self.dosing_regime_id, None)
        ).exists()
        if not dosing_regime_created:
            self.dosing_regime.copy_across_assessments(cw)
        self.dosing_regime_id = cw[DosingRegime.COPY_NAME][self.dosing_regime_id]
        self.save()

    def get_study(self):
        return self.experiment.get_study()


class DosingRegime(models.Model):

    objects = managers.DosingRegimeManager()

    ROUTE_EXPOSURE_CHOICES = (
        ("OR", "Oral"),
        ("OC", "Oral capsule"),
        ("OD", "Oral diet"),
        ("OG", "Oral gavage"),
        ("OW", "Oral drinking water"),
        ("I", "Inhalation"),
        ("IG", "Inhalation - gas"),
        ("IR", "Inhalation - particle"),
        ("IA", "Inhalation - vapor"),
        ("D", "Dermal"),
        ("SI", "Subcutaneous injection"),
        ("IP", "Intraperitoneal injection"),
        ("IV", "Intravenous injection"),
        ("IO", "in ovo"),
        ("P", "Parental"),
        ("W", "Whole body"),
        ("M", "Multiple"),
        ("U", "Unknown"),
        ("O", "Other"),
    )
    ROUTE_EXPOSURE_CHOICES_DICT = {el[0]: el[1] for el in ROUTE_EXPOSURE_CHOICES}

    POSITIVE_CONTROL_CHOICES = ((True, "Yes"), (False, "No"), (None, "Unknown"))

    NEGATIVE_CONTROL_CHOICES = (
        ("NR", "Not-reported"),
        ("UN", "Untreated"),
        ("VT", "Vehicle-treated"),
        ("B", "Untreated + Vehicle-treated"),
        ("N", "No"),
    )

    TEXT_CLEANUP_FIELDS = (
        "description",
        "duration_exposure_text",
    )

    dosed_animals = models.OneToOneField(
        AnimalGroup, related_name="dosed_animals", on_delete=models.SET_NULL, blank=True, null=True
    )
    route_of_exposure = models.CharField(
        max_length=2,
        choices=ROUTE_EXPOSURE_CHOICES,
        help_text="Primary route of exposure. If multiple primary-exposures, describe in notes-field below",
    )
    duration_exposure = models.FloatField(
        verbose_name="Exposure duration (days)",
        help_text="Length of exposure period (fractions allowed), used for sorting in visualizations. For single-dose or multiple-dose/same day gavage studies, 1.",
        blank=True,
        null=True,
    )
    duration_exposure_text = models.CharField(
        verbose_name="Exposure duration (text)",
        max_length=128,
        blank=True,
        help_text="Length of time between start of exposure and outcome assessment, "
        "in days when &lt;7 (e.g., 5d), weeks when &ge;7 days to 12 weeks (e.g., "
        "1wk, 12wk), or months when &gt;12 weeks (e.g., 15mon). For repeated "
        'measures use descriptions such as "1, 2 and 3 wk".  For inhalations '
        'studies, also include hours per day and days per week, e.g., "13wk '
        '(6h/d, 7d/wk)." This field is commonly used in visualizations, so '
        "use abbreviations (h, d, wk, mon, y) and no spaces between numbers "
        "to save space. For reproductive and developmental studies, where "
        'possible instead include abbreviated age descriptions such as "GD1-10" '
        'or "GD2-PND10". For gavage studies, include the number of doses, e.g. '
        '"1wk (1dose/d, 5d/wk)" or "2doses" for a single-day experiment.',
    )
    duration_observation = models.FloatField(
        verbose_name="Exposure-outcome duration",
        help_text="Optional: Numeric length of time between start of exposure and outcome assessment in days. "
        + "This field may be used to sort studies which is why days are used as a common metric.",
        blank=True,
        null=True,
    )
    num_dose_groups = models.PositiveSmallIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        verbose_name="Number of Dose Groups",
        help_text="Number of dose groups, plus control",
    )
    positive_control = models.BooleanField(
        choices=POSITIVE_CONTROL_CHOICES,
        default=False,
        help_text="Was a positive control used?",
        null=True,
        blank=True,
    )
    negative_control = models.CharField(
        max_length=2,
        default="VT",
        choices=NEGATIVE_CONTROL_CHOICES,
        help_text="Description of negative-controls used",
    )
    description = models.TextField(
        blank=True,
        help_text="Cut and paste from methods, use quotation marks around all "
        "text directly copy/pasted from paper. Also summarize results "
        "of any analytical work done to confirm dose, stability, etc. "
        "This can be a narrative summary of tabular information, "
        "e.g., \"Author's present data on the target and actual concentration "
        "(Table 1; means &plusmn; SD for entire 13-week period) and the values are "
        'very close." ',
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = "dose_regime"
    BREADCRUMB_PARENT = "dosed_animals"

    def __str__(self):
        return f"{self.dosed_animals} {self.get_route_of_exposure_display()}"

    def get_absolute_url(self):
        return self.dosed_animals.get_absolute_url()

    def get_assessment(self):
        return self.dosed_animals.get_assessment()

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @property
    def dose_groups(self):
        if not hasattr(self, "_dose_groups"):
            self._dose_groups = DoseGroup.objects.select_related("dose_units").filter(
                dose_regime=self.pk
            )
        return self._dose_groups

    def isAnimalsDosed(self, animal_group):
        return self.dosed_animals == animal_group

    @staticmethod
    def flat_complete_header_row():
        return (
            "dosing_regime-id",
            "dosing_regime-dosed_animals",
            "dosing_regime-route_of_exposure",
            "dosing_regime-duration_exposure",
            "dosing_regime-duration_exposure_text",
            "dosing_regime-duration_observation",
            "dosing_regime-num_dose_groups",
            "dosing_regime-positive_control",
            "dosing_regime-negative_control",
            "dosing_regime-description",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            AnimalGroup.get_relation_id(ser["dosed_animals"]),
            ser["route_of_exposure"],
            ser["duration_exposure"],
            ser["duration_exposure_text"],
            ser["duration_observation"],
            ser["num_dose_groups"],
            ser["positive_control"],
            ser["negative_control"],
            cleanHTML(ser["description"]),
        )

    def get_doses_json(self, json_encode=True):
        doses = []
        dgs = self.dose_groups.order_by("dose_units_id", "dose_group_id")
        for dg in dgs.distinct("dose_units"):
            dose_values = dgs.filter(dose_units=dg.dose_units).values_list("dose", flat=True)
            doses.append(
                {"id": dg.dose_units.id, "name": dg.dose_units.name, "values": list(dose_values)}
            )
        if json_encode:
            return json.dumps(doses, cls=HAWCDjangoJSONEncoder)
        else:
            return doses

    def copy_across_assessments(self, cw):
        children = list(self.dose_groups.all().order_by("id"))
        old_id = self.id
        self.id = None
        self.dosed_animals_id = cw[AnimalGroup.COPY_NAME].get(self.dosed_animals_id, None)
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)

    def get_study(self):
        return self.dosed_animals.get_study()


class DoseGroup(models.Model):
    objects = managers.DoseGroupManager()

    dose_regime = models.ForeignKey(DosingRegime, on_delete=models.CASCADE, related_name="doses")
    dose_units = models.ForeignKey("assessment.DoseUnits", on_delete=models.CASCADE)
    dose_group_id = models.PositiveSmallIntegerField()
    dose = models.FloatField(validators=[MinValueValidator(0)])
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    COPY_NAME = "doses"

    class Meta:
        ordering = ("dose_units", "dose_group_id")

    def __str__(self):
        return f"{self.dose} {self.dose_units}"

    @staticmethod
    def flat_complete_data_row(ser_full, units, idx):
        cols = []
        ser = [v for v in ser_full if v["dose_group_id"] == idx]
        for unit in units:
            v = None
            for s in ser:
                if s["dose_units"]["name"] == unit:
                    v = s["dose"]
                    break

            cols.append(v)

        return cols

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.dose_regime_id = cw[DosingRegime.COPY_NAME][self.dose_regime_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


class Endpoint(BaseEndpoint):
    objects = managers.EndpointManager()

    TEXT_CLEANUP_FIELDS = (
        "name",
        "system",
        "organ",
        "effect",
        "effect_subtype",
        "observation_time_text",
        "data_location",
        "response_units",
        "statistical_test",
        "diagnostic",
        "trend_value",
        "results_notes",
        "endpoint_notes",
        "litter_effect_notes",
    )
    TERM_FIELD_MAPPING = {
        "name": "name_term_id",
        "system": "system_term_id",
        "organ": "organ_term_id",
        "effect": "effect_term_id",
        "effect_subtype": "effect_subtype_term_id",
    }

    DATA_TYPE_CONTINUOUS = "C"
    DATA_TYPE_DICHOTOMOUS = "D"
    DATA_TYPE_PERCENT_DIFFERENCE = "P"
    DATA_TYPE_DICHOTOMOUS_CANCER = "DC"
    DATA_TYPE_NOT_REPORTED = "NR"

    DATA_TYPE_CHOICES = (
        (DATA_TYPE_CONTINUOUS, "Continuous"),
        (DATA_TYPE_DICHOTOMOUS, "Dichotomous"),
        (DATA_TYPE_PERCENT_DIFFERENCE, "Percent Difference"),
        (DATA_TYPE_DICHOTOMOUS_CANCER, "Dichotomous Cancer"),
        (DATA_TYPE_NOT_REPORTED, "Not reported"),
    )

    MONOTONICITY_CHOICES = (
        (8, "--"),
        (0, "N/A, single dose level study"),
        (1, "N/A, no effects detected"),
        (2, "visual appearance of monotonicity"),
        (3, "monotonic and significant trend"),
        (4, "visual appearance of non-monotonicity"),
        (6, "no pattern/unclear"),
    )

    VARIANCE_TYPE_CHOICES = ((0, "NA"), (1, "SD"), (2, "SE"), (3, "NR"))

    VARIANCE_NAME = {
        0: "N/A",
        1: "Standard Deviation",
        2: "Standard Error",
        3: "Not Reported",
    }

    OBSERVATION_TIME_UNITS = (
        (0, "not reported"),
        (1, "seconds"),
        (2, "minutes"),
        (3, "hours"),
        (4, "days"),
        (5, "weeks"),
        (6, "months"),
        (9, "years"),
        (7, "post-natal day (PND)"),
        (8, "gestational day (GD)"),
    )

    TREND_RESULT_CHOICES = (
        (0, "not applicable"),
        (1, "not significant"),
        (2, "significant"),
        (3, "not reported"),
    )

    ADVERSE_DIRECTION_CHOICES = (
        (3, "increase from reference/control group"),
        (2, "decrease from reference/control group"),
        (1, "any change from reference/control group"),
        (0, "unclear"),
        (4, "---"),
    )

    LITTER_EFFECT_CHOICES = (
        ("NA", "Not applicable"),
        ("NR", "Not reported"),
        ("YS", "Yes, statistical control"),
        ("YD", "Yes, study-design"),
        ("N", "No"),
        ("O", "Other"),
    )

    animal_group = models.ForeignKey(
        AnimalGroup, on_delete=models.CASCADE, related_name="endpoints"
    )
    name_term = models.ForeignKey(
        Term, related_name="endpoint_name_terms", on_delete=models.SET_NULL, blank=True, null=True
    )
    system = models.CharField(max_length=128, blank=True, help_text="Relevant biological system")
    system_term = models.ForeignKey(
        Term, related_name="endpoint_system_terms", on_delete=models.SET_NULL, blank=True, null=True
    )
    organ = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Organ (and tissue)",
        help_text="Relevant organ or tissue",
    )
    organ_term = models.ForeignKey(
        Term, related_name="endpoint_organ_terms", on_delete=models.SET_NULL, blank=True, null=True
    )
    effect = models.CharField(
        max_length=128, blank=True, help_text="Effect, using common-vocabulary"
    )
    effect_term = models.ForeignKey(
        Term, related_name="endpoint_effect_terms", on_delete=models.SET_NULL, blank=True, null=True
    )
    effect_subtype = models.CharField(
        max_length=128, blank=True, help_text="Effect subtype, using common-vocabulary"
    )
    effect_subtype_term = models.ForeignKey(
        Term,
        related_name="endpoint_effect_subtype_terms",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    litter_effects = models.CharField(
        max_length=2,
        choices=LITTER_EFFECT_CHOICES,
        default="NA",
        help_text='Type of controls used for litter-effects. The "No" response '
        + "will be infrequently used. More typically the information will be "
        + '"Not reported" and assumed not considered. Only use "No" if it '
        + "is explicitly mentioned in the study that litter was not controlled for.",
    )
    litter_effect_notes = models.CharField(
        max_length=128,
        help_text="Any additional notes describing how litter effects were controlled",
        blank=True,
    )
    observation_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Numeric value of the time an observation was reported; "
        "optional, should be recorded if the same effect was measured multiple times.",
    )
    observation_time_units = models.PositiveSmallIntegerField(
        default=0, choices=OBSERVATION_TIME_UNITS
    )
    observation_time_text = models.CharField(
        max_length=64, blank=True, help_text='Text for reported observation time (ex: "60-90 PND")',
    )
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
        '(ex: "Figure 1", "Table 2", "Text, p. 24", "Figure '
        '1 and Text, p.24")',
    )
    expected_adversity_direction = models.PositiveSmallIntegerField(
        choices=ADVERSE_DIRECTION_CHOICES,
        default=4,
        verbose_name="Expected response adversity direction",
        help_text="Response direction which would be considered adverse",
    )
    response_units = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Response units",
        help_text="Units the response was measured in (i.e., \u03BCg/dL, % control, etc.)",
    )
    data_type = models.CharField(
        max_length=2, choices=DATA_TYPE_CHOICES, default="C", verbose_name="Dataset type",
    )
    variance_type = models.PositiveSmallIntegerField(default=1, choices=VARIANCE_TYPE_CHOICES)
    confidence_interval = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Confidence interval (CI)",
        help_text="A 95% CI is written as 0.95.",
    )
    NOEL = models.SmallIntegerField(
        verbose_name="NOEL", default=-999, help_text="No observed effect level"
    )
    LOEL = models.SmallIntegerField(
        verbose_name="LOEL", default=-999, help_text="Lowest observed effect level"
    )
    FEL = models.SmallIntegerField(verbose_name="FEL", default=-999, help_text="Frank effect level")
    data_reported = models.BooleanField(
        default=True,
        help_text="Dose-response data for endpoint are available in the literature source",
    )
    data_extracted = models.BooleanField(
        default=True,
        help_text="Dose-response data for endpoint are extracted from literature into HAWC",
    )
    values_estimated = models.BooleanField(
        default=False,
        help_text="Response values were estimated using a digital ruler or other methods",
    )
    monotonicity = models.PositiveSmallIntegerField(default=8, choices=MONOTONICITY_CHOICES)
    statistical_test = models.CharField(
        max_length=256,
        blank=True,
        help_text="Short description of statistical analysis techniques used, e.g., "
        "Fisher Exact Test, ANOVA, Chi Square, Peto's test, none conducted",
    )
    trend_value = models.FloatField(
        null=True, blank=True, help_text="Numerical result for trend-test, if available"
    )
    trend_result = models.PositiveSmallIntegerField(default=3, choices=TREND_RESULT_CHOICES)
    diagnostic = models.TextField(
        verbose_name="Endpoint Name in Study",
        blank=True,
        help_text="List the endpoint/adverse outcome name as used in the study. "
        "This will help during QA/QC of the extraction to the original "
        "study in cases where the endpoint/adverse outcome name is "
        "adjusted for consistency across studies or assessments.",
    )
    power_notes = models.TextField(
        blank=True, help_text="Power of study-design to detect change from control"
    )
    results_notes = models.TextField(
        blank=True,
        help_text="""
            Qualitative description of the results. This field can be
            left blank if there is no need to further describe numerically
            extracted findings, e.g., organ or body weights. Use this
            field to describe findings such as the type and severity
            of histopathology or malformations not otherwise captured
            in the numerical data extraction. Also use this field to cut
            and paste findings described only in text in the study. If
            coding is used to create exposure-response arrays, then add
            this comment in bold font at the start of the text box entry
            <strong>"For exposure-response array data display purposes, the following
            results were coded (control and no effect findings were coded as
            "0", treatment-related increases were coded as "1", and
            treatment-related decreases were coded as "-1"."</strong>
            """,
    )
    endpoint_notes = models.TextField(
        blank=True,
        verbose_name="Methods",
        help_text="Cut and paste from methods, use quotation marks around all "
        "text directly copy/pasted from paper. Include all methods "
        "pertinent to measuring ALL outcomes, including statistical "
        "methods. This will make it easier to copy from existing HAWC "
        "endpoints to create new endpoints for a study.",
    )
    additional_fields = models.TextField(default="{}")

    COPY_NAME = "endpoints"
    BREADCRUMB_PARENT = "animal_group"

    class Meta:
        ordering = ("id",)

    def get_update_url(self):
        return reverse("animal:endpoint_update", args=[self.pk])

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @classmethod
    def heatmap_df(cls, assessment_id: int, published_only: bool) -> pd.DataFrame:
        filters: Dict[str, Any] = {"assessment_id": assessment_id}
        if published_only:
            filters["animal_group__experiment__study__published"] = True
        columns = {
            "animal_group__experiment__study_id": "study id",
            "animal_group__experiment__study__short_citation": "study citation",
            "animal_group__experiment__study__study_identifier": "study identifier",
            "animal_group__experiment_id": "experiment id",
            "animal_group__experiment__name": "experiment name",
            "animal_group__experiment__type": "experiment type",
            "animal_group__experiment__cas": "experiment cas",
            "animal_group__experiment__dtxsid": "experiment dtxsid",
            "animal_group__experiment__chemical": "experiment chemical",
            "animal_group_id": "animal group id",
            "animal_group__name": "animal group name",
            "animal_group__species__name": "species",
            "animal_group__strain__name": "strain",
            "animal_group__sex": "sex",
            "animal_group__generation": "generation",
            "animal_group__dosing_regime__route_of_exposure": "route of exposure",
            "id": "endpoint id",
            "system": "system",
            "organ": "organ",
            "effect": "effect",
            "effect_subtype": "effect subtype",
            "name": "endpoint name",
            "observation_time_text": "observation time",
        }
        qs = (
            cls.objects.select_related(
                "animal_group",
                "animal_group__dosing_regime",
                "animal_group__species",
                "animal_group__strain",
                "animal_group__experiment",
                "animal_group__experiment__study",
            )
            .filter(**filters)
            .values_list(*columns.keys())
            .order_by("id")
        )
        df = pd.DataFrame(data=list(qs), columns=columns.values())
        df["route of exposure"] = df["route of exposure"].map(
            DosingRegime.ROUTE_EXPOSURE_CHOICES_DICT
        )
        df["sex"] = df["sex"].map(AnimalGroup.SEX_DICT)
        df["generation"] = df["generation"].map(AnimalGroup.GENERATION_DICT)
        df["experiment type"] = df["experiment type"].map(Experiment.EXPERIMENT_TYPE_DICT)

        # get animal-group values
        df = (
            df.merge(
                AnimalGroup.objects.animal_description(assessment_id),
                how="left",
                left_on="animal group id",
                right_on="animal group id",
            )
            .pipe(df_move_column, "animal description", "animal group name")
            .pipe(df_move_column, "animal description, with n", "animal description")
            .pipe(df_move_column, "treatment period", "experiment type")
        )

        # overall risk of bias evaluation
        FinalRiskOfBiasScore = apps.get_model("materialized", "FinalRiskOfBiasScore")
        df2 = FinalRiskOfBiasScore.objects.overall_endpoint_scores(assessment_id)
        if df2 is not None:
            df = (
                df.merge(df2, how="left", left_on="endpoint id", right_on="endpoint id")
                .pipe(df_move_column, "overall study evaluation", "study identifier")
                .fillna("")
            )
        return df

    @classmethod
    def heatmap_doses_df(cls, assessment_id: int, published_only: bool) -> pd.DataFrame:
        df1 = cls.heatmap_df(assessment_id, published_only).set_index("endpoint id")

        columns = "dose units id|dose units name|doses|noel|loel|fel|bmd|bmdl".split("|")
        df2 = cls.objects.endpoint_df(assessment_id, published_only).set_index("endpoint id")[
            columns
        ]

        df3 = (
            df1.merge(df2, how="left", left_index=True, right_index=True)
            .reset_index()
            .pipe(df_move_column, "endpoint id", "route of exposure")
        )
        return df3

    @classmethod
    def heatmap_study_df(cls, assessment_id: int, published_only: bool) -> pd.DataFrame:
        def unique_items(els):
            return "|".join(sorted(set(el for el in els if el is not None)))

        # get all studies,even if no endpoint data is extracted
        filters: Dict[str, Any] = {"assessment_id": assessment_id, "bioassay": True}
        if published_only:
            filters["published"] = True
        columns = {
            "id": "study id",
            "short_citation": "study citation",
            "study_identifier": "study identifier",
        }
        qs = Study.objects.filter(**filters).values_list(*columns.keys()).order_by("id")
        df1 = pd.DataFrame(data=list(qs), columns=columns.values()).set_index("study id")

        # rollup endpoint-level data to studies
        df2 = cls.heatmap_df(assessment_id, published_only)
        aggregates = {
            "experiment type": unique_items,
            "experiment chemical": unique_items,
            "species": unique_items,
            "sex": unique_items,
            "strain": unique_items,
            "route of exposure": unique_items,
            "system": unique_items,
            "organ": unique_items,
            "effect": unique_items,
        }
        if "overall study evaluation" in df2:
            aggregates["overall study evaluation"] = unique_items
        df2 = df2.groupby("study id").agg(aggregates)

        # rollup dose-units to study
        values = dict(
            dose_regime__dosed_animals__experiment__study_id="study id",
            dose_units__name="dose units",
        )
        qs = (
            DoseGroup.objects.filter(
                dose_regime__dosed_animals__experiment__study__assessment_id=assessment_id
            )
            .select_related("dose_regime__dosed_animals__experiment__study",)
            .values_list(*values.keys())
            .distinct("dose_regime__dosed_animals__experiment__study_id", "dose_units__id")
            .order_by()
        )
        df3 = (
            pd.DataFrame(data=qs, columns=values.values())
            .groupby("study id")
            .agg({"dose units": unique_items})
        )

        # merge all the data frames together
        df = (
            df1.merge(df2, how="left", left_index=True, right_index=True)
            .merge(df3, how="left", left_index=True, right_index=True)
            .fillna("")
            .reset_index()
        )
        return df

    @classmethod
    def get_vocabulary_settings(cls, assessment: Assessment, form: ModelForm) -> str:
        return json.dumps(
            {
                "debug": False,
                "vocabulary": assessment.vocabulary,
                "vocabulary_display": assessment.get_vocabulary_display(),
                "object": {
                    "system": form.initial.get("system", ""),
                    "organ": form.initial.get("organ", ""),
                    "effect": form.initial.get("effect", ""),
                    "effect_subtype": form.initial.get("effect_subtype", ""),
                    "name": form.initial.get("name", ""),
                    "system_term_id": form.initial.get("system_term", None),
                    "organ_term_id": form.initial.get("organ_term", None),
                    "effect_term_id": form.initial.get("effect_term", None),
                    "effect_subtype_term_id": form.initial.get("effect_subtype_term", None),
                    "name_term_id": form.initial.get("name_term", None),
                },
            }
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("animal:endpoint_detail", args=(self.pk,))

    def save(self, *args, **kwargs):
        # ensure our controlled vocabulary terms don't have leading/trailing whitespace
        self.system = self.system.strip()
        self.organ = self.organ.strip()
        self.effect = self.effect.strip()
        self.effect_subtype = self.effect_subtype.strip()
        self.name = self.name.strip()
        super().save(*args, **kwargs)

    @property
    def dose_response_available(self):
        return self.data_reported and self.data_extracted

    @property
    def bmd_modeling_possible(self):
        return self.dose_response_available and self.groups.count() >= 3

    def get_doses_json(self, json_encode=True):
        """
        Return a dictionary containing the doses available for the selected
        endpoint, and also saves a copy to the instance.
        """
        if not hasattr(self, "doses"):
            self.doses = self.animal_group.get_doses_json(False)
        if json_encode:
            return json.dumps(self.doses, cls=HAWCDjangoJSONEncoder)
        return self.doses

    @property
    def variance_name(self):
        return Endpoint.VARIANCE_NAME.get(self.variance_type, "N/A")

    @staticmethod
    def max_dose_count(queryset):
        max_val = 0
        qs = queryset.annotate(max_egs=models.Count("groups", distinct=True)).values_list(
            "max_egs", flat=True
        )
        if len(qs) > 0:
            max_val = max(qs)
        return max_val

    @staticmethod
    def get_qs_json(queryset, json_encode=True):
        endpoints = [e.get_json(json_encode=False) for e in queryset]
        if json_encode:
            return json.dumps(endpoints, cls=HAWCDjangoJSONEncoder)
        else:
            return endpoints

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def get_assessment(self):
        return self.assessment

    def litter_effect_required(self):
        return self.animal_group.experiment.type in ["Rp", "1r", "2r", "Dv"]

    def litter_effect_optional(self):
        return self.litter_effect_required() or self.animal_group.experiment.type == "Ot"

    @property
    def dataset_increasing(self):
        """
        Check used to determine if data are increasing or dataset_increasing.
        Returns True if data are increasing or false if otherwise. Only used
        with continuous datasets.
        """
        # dichotomous datasets increase by definition,
        # exit early for not-reported
        if self.data_type in ["D", "DC", "NR"]:
            return True
        change = 0
        resps = self.groups.values_list("response", flat=True)
        resps = [x for x in resps if x is not None]
        for i in range(1, len(resps)):
            change += resps[i] - resps[0]
        return change >= 0

    @staticmethod
    def flat_complete_header_row():
        return (
            "endpoint-id",
            "endpoint-url",
            "endpoint-name",
            "endpoint-effects",
            "endpoint-system",
            "endpoint-organ",
            "endpoint-effect",
            "endpoint-effect_subtype",
            "endpoint-name_term_id",
            "endpoint-system_term_id",
            "endpoint-organ_term_id",
            "endpoint-effect_term_id",
            "endpoint-effect_subtype_term_id",
            "endpoint-litter_effects",
            "endpoint-litter_effect_notes",
            "endpoint-observation_time",
            "endpoint-observation_time_units",
            "endpoint-observation_time_text",
            "endpoint-data_location",
            "endpoint-response_units",
            "endpoint-data_type",
            "endpoint-variance_type",
            "endpoint-confidence_interval",
            "endpoint-data_reported",
            "endpoint-data_extracted",
            "endpoint-values_estimated",
            "endpoint-expected_adversity_direction",
            "endpoint-monotonicity",
            "endpoint-statistical_test",
            "endpoint-trend_value",
            "endpoint-trend_result",
            "endpoint-diagnostic",
            "endpoint-power_notes",
            "endpoint-results_notes",
            "endpoint-endpoint_notes",
            "endpoint-additional_fields",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["url"],
            ser["name"],
            "|".join([d["name"] for d in ser["effects"]]),
            ser["system"],
            ser["organ"],
            ser["effect"],
            ser["effect_subtype"],
            ser["name_term"],
            ser["system_term"],
            ser["organ_term"],
            ser["effect_term"],
            ser["effect_subtype_term"],
            ser["litter_effects"],
            ser["litter_effect_notes"],
            ser["observation_time"],
            ser["observation_time_units"],
            ser["observation_time_text"],
            ser["data_location"],
            ser["response_units"],
            ser["data_type"],
            ser["variance_name"],
            ser["confidence_interval"],
            ser["data_reported"],
            ser["data_extracted"],
            ser["values_estimated"],
            ser["expected_adversity_direction_text"],
            ser["monotonicity"],
            ser["statistical_test"],
            ser["trend_value"],
            ser["trend_result"],
            ser["diagnostic"],
            ser["power_notes"],
            cleanHTML(ser["results_notes"]),
            cleanHTML(ser["endpoint_notes"]),
            json.dumps(ser["additional_fields"]),
        )

    @staticmethod
    def get_docx_template_context(assessment, queryset):
        """
        Given a queryset of endpoints, invert the cached results to build
        a top-down data hierarchy from study to endpoint. We use this
        approach since our endpoints are cached, so while it may require
        more computation, its close to free on database access.
        """

        endpoints = [SerializerHelper.get_serialized(obj, json=False) for obj in queryset]
        studies = {}

        # flip dictionary nesting
        for thisEp in endpoints:
            thisAG = thisEp["animal_group"]
            thisExp = thisEp["animal_group"]["experiment"]
            thisStudy = thisEp["animal_group"]["experiment"]["study"]

            study = studies.get(thisStudy["id"])
            if study is None:
                study = thisStudy
                study["exps"] = {}
                studies[study["id"]] = study

            exp = study["exps"].get(thisExp["id"])
            if exp is None:
                exp = thisExp
                exp["ags"] = {}
                study["exps"][exp["id"]] = exp

            ag = exp["ags"].get(thisAG["id"])
            if ag is None:
                ag = thisAG
                ag["eps"] = {}
                exp["ags"][ag["id"]] = ag

            ep = ag["eps"].get(thisEp["id"])
            if ep is None:
                ep = thisEp
                ag["eps"][ep["id"]] = ep

        # convert value dictionaries to lists
        studies = sorted(list(studies.values()), key=lambda obj: (obj["short_citation"].lower()))
        for study in studies:
            study["exps"] = sorted(
                list(study["exps"].values()), key=lambda obj: (obj["name"].lower())
            )
            for exp in study["exps"]:
                exp["ags"] = sorted(
                    list(exp["ags"].values()), key=lambda obj: (obj["name"].lower())
                )
                for ag in exp["ags"]:
                    ag["eps"] = sorted(
                        list(ag["eps"].values()), key=lambda obj: (obj["name"].lower())
                    )

        return {
            "assessment": AssessmentSerializer().to_representation(assessment),
            "studies": studies,
        }

    @staticmethod
    def setMaximumPercentControlChange(ep):
        """
        For each endpoint, return the maximum absolute-change percent control
        for that endpoint, or 0 if it cannot be calculated. Useful for
        ordering data-pivot results.
        """
        val = 0
        changes = [
            g["percentControlMean"]
            for g in ep["groups"]
            if tryParseInt(g["percentControlMean"], default=False)
        ]
        if len(changes) > 0:
            min_ = min(changes)
            max_ = max(changes)
            val = min_ if abs(min_) > abs(max_) else max_

        ep["percentControlMaxChange"] = val

    def get_latest_bmd_session(self):
        try:
            return self.bmd_sessions.latest()
        except ObjectDoesNotExist:
            return None

    def get_selected_bmd_model(self):
        try:
            return self.bmd_model
        except ObjectDoesNotExist:
            return None

    def copy_across_assessments(self, cw):
        children = chain(
            list(self.groups.all().order_by("id")), list(self.bmd_sessions.all().order_by("id")),
        )
        effects = list(self.effects.all().order_by("id"))

        old_id = self.id
        new_assessment_id = cw[Assessment.COPY_NAME][self.assessment_id]

        # copy base endpoint
        base = self.baseendpoint_ptr
        base.id = None
        base.assessment_id = new_assessment_id
        base.save()

        # copy endpoint
        self.id = None
        self.baseendpoint_ptr = base
        self.assessment_id = new_assessment_id
        self.animal_group_id = cw[AnimalGroup.COPY_NAME][self.animal_group_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id

        self.effects.set(effects)

        # copy other children
        for child in children:
            child.copy_across_assessments(cw)

    def get_study(self):
        return self.animal_group.get_study()

    def get_noel_names(self):
        return self.assessment.get_noel_names()


class ConfidenceIntervalsMixin:
    """
    Mixin class which calculates standard deviation and confidence intervals
    for django models.
    """

    @property
    def hasVariance(self):
        return self.variance is not None

    @staticmethod
    def stdev(variance_type, variance, n):
        # calculate stdev given re
        if variance_type == 1:
            return variance
        elif variance_type == 2 and variance is not None and n is not None:
            return variance * math.sqrt(n)
        else:
            return None

    def getStdev(self, variance_type=None):
        """ Return the stdev of an endpoint-group, given the variance type. """
        if not hasattr(self, "_stdev"):

            # don't hit DB unless we need to
            if variance_type is None:
                variance_type = self.endpoint.variance_type

            self._stdev = self.stdev(variance_type, self.variance, self.n)

        return self._stdev

    @classmethod
    def getStdevs(cls, variance_type, egs):
        for eg in egs:
            eg["stdev"] = cls.stdev(variance_type, eg["variance"], eg["n"])

    @staticmethod
    def percentControl(data_type, egs):
        """
        Expects a dictionary of endpoint groups and the endpoint data-type.
        Appends results to the dictionary for each endpoint-group.

        Calculates a 95% confidence interval for the percent-difference from
        control, taking into account variance from both groups using a
        Fisher Information Matrix, assuming independent normal distributions.
        """
        for i, eg in enumerate(egs):
            mean = low = high = None
            if data_type == "C":

                if i == 0:
                    n_1 = eg["n"]
                    mu_1 = eg["response"]
                    sd_1 = eg.get("stdev")

                n_2 = eg["n"]
                mu_2 = eg["response"]
                sd_2 = eg.get("stdev")

                if mu_1 is not None and mu_2 is not None and mu_1 > 0 and mu_2 > 0:
                    mean = (mu_2 - mu_1) / mu_1 * 100.0
                    if sd_1 and sd_2 and n_1 and n_2:
                        sd = math.sqrt(
                            pow(mu_1, -2)
                            * (
                                (pow(sd_2, 2) / n_2)
                                + (pow(mu_2, 2) * pow(sd_1, 2)) / (n_1 * pow(mu_1, 2))
                            )
                        )
                        ci = (1.96 * sd) * 100
                        rng = sorted([mean - ci, mean + ci])
                        low = rng[0]
                        high = rng[1]

            elif data_type == "P":
                mean = eg["response"]
                low = eg["lower_ci"]
                high = eg["upper_ci"]

            eg.update(percentControlMean=mean, percentControlLow=low, percentControlHigh=high)

    @staticmethod
    def getConfidenceIntervals(data_type, egs):
        """
        Expects a dictionary of endpoint groups and the endpoint data-type.
        Appends results to the dictionary for each endpoint-group.
        """
        for eg in egs:
            lower_ci = eg.get("lower_ci")
            upper_ci = eg.get("upper_ci")
            n = eg.get("n")
            update = False

            if lower_ci is not None or upper_ci is not None or n is None or n <= 0:
                continue

            if data_type == "C" and eg["response"] is not None and eg["stdev"] is not None:
                """
                Two-tailed t-test, assuming 95% confidence interval.
                """
                se = eg["stdev"] / math.sqrt(n)
                change = stats.t.ppf(0.975, max(n - 1, 1)) * se
                lower_ci = eg["response"] - change
                upper_ci = eg["response"] + change
                update = True
            elif data_type in ["D", "DC"] and eg["incidence"] is not None:
                """
                Procedure adds confidence intervals to dichotomous datasets.
                Taken from bmds231_manual.pdf, pg 124-5

                LL = {(2np + z2 - 1) - z*sqrt[z2 - (2+1/n) + 4p(nq+1)]}/[2*(n+z2)]
                UL = {(2np + z2 + 1) + z*sqrt[z2 + (2-1/n) + 4p(nq-1)]}/[2*(n+z2)]

                - p = the observed proportion
                - n = the total number in the group in question
                - z = Z(1-alpha/2) is the inverse standard normal cumulative
                      distribution function evaluated at 1-alpha/2
                - q = 1-p.

                The error bars shown in BMDS plots use alpha = 0.05 and so
                represent the 95% confidence intervals on the observed
                proportions (independent of model).
                """
                p = eg["incidence"] / float(n)
                z = stats.norm.ppf(0.975)
                q = 1.0 - p

                lower_ci = round(
                    (
                        (2 * n * p + 2 * z - 1)
                        - z * math.sqrt(2 * z - (2 + 1 / n) + 4 * p * (n * q + 1))
                    )
                    / (2 * (n + 2 * z)),
                    3,
                )
                upper_ci = round(
                    (
                        (2 * n * p + 2 * z + 1)
                        + z * math.sqrt(2 * z + (2 + 1 / n) + 4 * p * (n * q - 1))
                    )
                    / (2 * (n + 2 * z)),
                    3,
                )

                update = True

            if update:
                eg.update(lower_ci=lower_ci, upper_ci=upper_ci)

    @staticmethod
    def get_incidence_summary(data_type, egs):
        # For plotting purposes, present incidence numbers as percentage and
        # generate a pretty-printing format for dichotomous data
        for eg in egs:
            additions = dict(
                dichotomous_summary="-",
                percent_affected=None,
                percent_lower_ci=None,
                percent_upper_ci=None,
            )
            n = eg["n"]
            inc = eg["incidence"]
            if data_type in ["D", "DC"] and n is not None and n > 0 and inc is not None:
                additions.update(
                    dichotomous_summary=f"{inc}/{n} ({inc / n * 100:.1f}%)",
                    percent_affected=inc / n * 100,
                    percent_lower_ci=eg["lower_ci"] * 100,
                    percent_upper_ci=eg["upper_ci"] * 100,
                )

            eg.update(**additions)


class EndpointGroup(ConfidenceIntervalsMixin, models.Model):
    objects = managers.EndpointGroupManager()

    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE, related_name="groups")
    dose_group_id = models.IntegerField()
    n = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    incidence = models.PositiveSmallIntegerField(
        blank=True, null=True, validators=[MinValueValidator(0)]
    )
    response = models.FloatField(blank=True, null=True)
    variance = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
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
    significant = models.BooleanField(
        default=False, verbose_name="Statistically significant from control"
    )
    significance_level = models.FloatField(
        null=True,
        blank=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name="Statistical significance level",
    )

    COPY_NAME = "groups"

    class Meta:
        ordering = ("endpoint", "dose_group_id")

    def clean(self):
        self.significant = self.significance_level is not None and self.significance_level > 0

    @property
    def isReported(self):
        return self.incidence is not None or self.response is not None

    @staticmethod
    def getNRangeText(ns):
        """
        Given a list of N values, return textual range of N values in the list.
        For example, may return "10-12", "7", or "NR".
        """
        if len(ns) == 0:
            return "NR"
        nmin = min(ns)
        nmax = max(ns)
        if nmin == nmax:
            if nmin is None:
                return "NR"
            else:
                return str(nmin)
        else:
            return f"{nmin}-{nmax}"

    @staticmethod
    def flat_complete_header_row():
        return (
            "endpoint_group-id",
            "endpoint_group-dose_group_id",
            "endpoint_group-n",
            "endpoint_group-incidence",
            "endpoint_group-response",
            "endpoint_group-variance",
            "endpoint_group-lower_ci",
            "endpoint_group-upper_ci",
            "endpoint_group-significant",
            "endpoint_group-significance_level",
            "endpoint_group-NOEL",
            "endpoint_group-LOEL",
            "endpoint_group-FEL",
        )

    @staticmethod
    def flat_complete_data_row(ser, endpoint):
        return (
            ser["id"],
            ser["dose_group_id"],
            ser["n"],
            ser["incidence"],
            ser["response"],
            ser["variance"],
            ser["lower_ci"],
            ser["upper_ci"],
            ser["significant"],
            ser["significance_level"],
            ser["dose_group_id"] == endpoint["NOEL"],
            ser["dose_group_id"] == endpoint["LOEL"],
            ser["dose_group_id"] == endpoint["FEL"],
        )

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.endpoint_id = cw[Endpoint.COPY_NAME][self.endpoint_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


reversion.register(Experiment)
reversion.register(AnimalGroup)
reversion.register(DosingRegime)
reversion.register(DoseGroup)
reversion.register(Endpoint, follow=("groups",))
reversion.register(EndpointGroup, follow=("endpoint",))
