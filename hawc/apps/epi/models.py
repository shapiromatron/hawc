import itertools
import json
import math
from operator import xor
from typing import Any

import pandas as pd
from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from reversion import revisions as reversion
from scipy.stats import t

from ..assessment.models import BaseEndpoint, DSSTox, EffectTag
from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper, df_move_column
from ..study.models import Study
from . import constants, managers

# version with no special formatting exists as sometimes it is used in a tag title attribute, e.g. for tooltips
HAWC_VIS_NOTE_UNSTYLED = "This field is commonly used in HAWC visualizations"
HAWC_VIS_NOTE = "<span class='important-note'>" + HAWC_VIS_NOTE_UNSTYLED + "</span>"
OPTIONAL_NOTE = "<span class='help-text-notes optional'>Optional</span>"


def formatHelpTextNotes(s):
    return f"<span class='help-text-notes'>{s}</span>"


class Criteria(models.Model):
    objects = managers.CriteriaManager()

    assessment = models.ForeignKey("assessment.Assessment", on_delete=models.CASCADE)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("description",)
        unique_together = ("assessment", "description")
        verbose_name_plural = "Criteria"

    def __str__(self):
        return self.description

    def get_assessment(self):
        return self.assessment


class Country(models.Model):
    objects = managers.CountryManager()

    code = models.CharField(blank=True, max_length=2)
    name = models.CharField(unique=True, max_length=64)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class AdjustmentFactor(models.Model):
    objects = managers.AdjustmentFactorManager()

    assessment = models.ForeignKey("assessment.Assessment", on_delete=models.CASCADE)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("assessment", "description")
        ordering = ("description",)

    def __str__(self):
        return self.description


class Ethnicity(models.Model):
    objects = managers.EthnicityManger()

    name = models.CharField(max_length=64, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Ethnicities"

    def __str__(self):
        return self.name


class StudyPopulationCriteria(models.Model):
    objects = managers.StudyPopulationCriteriaManager()

    criteria = models.ForeignKey("Criteria", on_delete=models.CASCADE, related_name="spcriteria")
    study_population = models.ForeignKey(
        "StudyPopulation", on_delete=models.CASCADE, related_name="spcriteria"
    )
    criteria_type = models.CharField(max_length=1, choices=constants.CriteriaType.choices)


class StudyPopulation(models.Model):
    objects = managers.StudyPopulationManager()

    CRITERIA_HELP_TEXTS = {
        "inclusion_criteria": "What criteria were used to determine an individual`s eligibility? Ex. at least 18 years old; born in the country of study; singleton pregnancy",
        "exclusion_criteria": "What criteria were used to exclude an individual from participation?  Ex. pre-existing medical conditions, pregnancy, use of medication",
        "confounding_criteria": OPTIONAL_NOTE,
    }

    TEXT_CLEANUP_FIELDS = (
        "name",
        "age_profile",
        "source",
        "region",
        "comments",
    )

    OUTCOME_GROUP_DESIGNS = ("CC", "NC")

    study = models.ForeignKey(
        "study.Study", on_delete=models.CASCADE, related_name="study_populations"
    )
    name = models.CharField(
        max_length=256,
        help_text="Name the population associated with the study, following the format <b>Study name (years study conducted), Country, number participants "
        + "(number male, number female, if relevant).</b> Ex. INUENDO (2002-2004), Greenland/Poland/Ukraine, 1,321 mother-infant pairs; "
        + "NHANES (2007-2010), U.S., 1,181 adults (672 men, 509 women). "
        + formatHelpTextNotes("Use men/women for adults (>=18), boys/girls for children (<18).")
        + formatHelpTextNotes("Note pregnant women if applicable.")
        + formatHelpTextNotes(
            "There may be multiple study populations within a single study, though this is typically unlikely."
        )
        + HAWC_VIS_NOTE,
    )
    design = models.CharField(
        max_length=2,
        choices=constants.Design.choices,
        help_text="Choose the most specific description of study design." + HAWC_VIS_NOTE,
    )
    age_profile = models.CharField(
        max_length=128,
        blank=True,
        help_text="State study population`s age category, with quantitative information (mean, median, SE, range) in parentheses where available. "
        + "Ex. Pregnancy (mean 31 years; SD 4 years); Newborn; Adulthood "
        + formatHelpTextNotes(
            'Use age categories "Fetal" (in utero), "Newborn" (at birth), "Neonatal" (0-4 weeks), '
            + '"Infancy" (0-12 months), "Childhood" (0-11 years), "Adolescence" (12-18 years), "Adulthood" '
            + "(>18 years); may be assessment specific."
        )
        + formatHelpTextNotes(
            'Note "Pregnancy" instead of "Adolescence" or "Adulthood" if applicable.'
        )
        + formatHelpTextNotes("If multiple, separate with semicolons.")
        + formatHelpTextNotes("Add units for quantitative measurements (days, months, years)."),
    )
    source = models.CharField(
        max_length=128,
        blank=True,
        help_text="Population source (General population, Occupational cohort, Superfund site, etc.). Ex. General population",
    )
    countries = models.ManyToManyField(Country, blank=True)
    region = models.CharField(max_length=128, blank=True, help_text=OPTIONAL_NOTE)
    state = models.CharField(max_length=128, blank=True, help_text=OPTIONAL_NOTE)
    eligible_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Eligible N",
        help_text=OPTIONAL_NOTE
        + "<span class='optional'>Number of individuals eligible based on study design and inclusion/exclusion criteria.</span>",
    )
    invited_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Invited N",
        help_text=OPTIONAL_NOTE
        + "<span class='optional'>Number of individuals initially asked to participate in the study.</span>",
    )
    participant_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Participant N",
        help_text="How many individuals participated in the study? Ex. 1321<br/>"
        + formatHelpTextNotes(
            "If mother-infant pairs, note number of pairs, not total individuals studied"
        ),
    )
    criteria = models.ManyToManyField(
        Criteria, through=StudyPopulationCriteria, related_name="populations"
    )
    comments = models.TextField(
        blank=True,
        help_text="Copy-paste text describing study population selection <br/>"
        + 'Ex. "Data and biospecimens were obtained from the Maternal Infant Research on Environmental Chemicals (MIREC) Study, '
        + "a trans-Canada cohort study of 2,001 pregnant women. Study participants were recruited from 10 Canadian cities between "
        + "2008 and 2011. Briefly, women were eligible for inclusion if the fetus was at <14 weeks` gestation at the time of recruitment "
        + "and they were ≥18 years of age, able to communicate in French or English, and planning on delivering at a local hospital. "
        + "Women with known fetal or chromosomal anomalies in the current pregnancy and women with a history of medical complications "
        + "(including renal disease, epilepsy, hepatitis, heart disease, pulmonary disease, cancer, hematological disorders, threatened "
        + 'spontaneous abortion, and illicit drug use) were excluded from the study."',
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study"

    @staticmethod
    def flat_complete_header_row():
        return (
            "sp-id",
            "sp-url",
            "sp-name",
            "sp-design",
            "sp-age_profile",
            "sp-source",
            "sp-countries",
            "sp-region",
            "sp-state",
            "sp-eligible_n",
            "sp-invited_n",
            "sp-participant_n",
            "sp-inclusion_criteria",
            "sp-exclusion_criteria",
            "sp-confounding_criteria",
            "sp-comments",
            "sp-created",
            "sp-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        def getCriteriaList(lst, filt):
            return "|".join(
                [d["description"] for d in [d for d in lst if d["criteria_type"] == filt]]
            )

        return (
            ser["id"],
            ser["url"],
            ser["name"],
            ser["design"],
            ser["age_profile"],
            ser["source"],
            "|".join([c["name"] for c in ser["countries"]]),
            ser["region"],
            ser["state"],
            ser["eligible_n"],
            ser["invited_n"],
            ser["participant_n"],
            getCriteriaList(ser["criteria"], "Inclusion"),
            getCriteriaList(ser["criteria"], "Exclusion"),
            getCriteriaList(ser["criteria"], "Confounding"),
            ser["comments"],
            ser["created"],
            ser["last_updated"],
        )

    class Meta:
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse("epi:sp_detail", args=(self.pk,))

    def get_assessment(self):
        return self.study.get_assessment()

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @property
    def inclusion_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="I")

    @property
    def exclusion_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="E")

    @property
    def confounding_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="C")

    def __str__(self):
        return self.name

    def can_create_sets(self):
        return self.design not in self.OUTCOME_GROUP_DESIGNS

    def get_study(self):
        return self.study


class Outcome(BaseEndpoint):
    objects = managers.OutcomeManager()

    TEXT_CLEANUP_FIELDS = (
        "name",
        "system",
        "effect",
        "effect_subtype",
    )

    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="outcomes"
    )
    system = models.CharField(
        max_length=128, blank=True, help_text="Primary biological system affected"
    )
    effect = models.CharField(
        max_length=128,
        blank=True,
        help_text="Effect, using common-vocabulary. Use title style (capitalize all words). Ex. Thyroid Hormones",
    )
    effect_subtype = models.CharField(
        max_length=128,
        blank=True,
        help_text="Effect subtype, using common-vocabulary. Use title style (capitalize all words). Ex. Absolute"
        + formatHelpTextNotes("This field is not mandatory; often no effect subtype is necessary"),
    )
    diagnostic = models.PositiveSmallIntegerField(choices=constants.Diagnostic.choices)
    diagnostic_description = models.TextField(
        help_text='Copy and paste diagnostic methods directly from study. Ex. "Birth weight (grams) was measured by trained midwives at delivery." '
        + formatHelpTextNotes("Use quotation marks around direct quotes from a study")
    )
    outcome_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Outcome N",
        help_text="Number of individuals for whom outcome was reported. Ex. 132",
    )
    age_of_measurement = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Age at outcome measurement",
        help_text="State study population`s age category at outcome measurement, with quantitative information "
        + "(mean, median, SE, range) in parentheses where available.<br/>"
        + "Ex. Pregnancy (mean 31 years;  SD 4 years); Newborn; Adulthood "
        + formatHelpTextNotes(
            'Use age categories "Fetal" (in utero), "Newborn" (at birth), '
            + '"Neonatal" (0-4 weeks), "Infancy" (0-12 months), "Childhood" (0-11 years), '
            + '"Adolescence" (12-18 years), "Adulthood" (>18 years); may be assessment specific'
        )
        + formatHelpTextNotes(
            'Note "Pregnancy" instead of "Adolescence" or "Adulthood" if applicable'
        )
        + formatHelpTextNotes("If multiple, separate with semicolons")
        + formatHelpTextNotes("Add units for quantitative measurements (days, months, years)"),
    )
    summary = models.TextField(
        blank=True,
        help_text="Provide additional outcome or extraction details if necessary. Ex. No association (data not shown)",
    )

    BREADCRUMB_PARENT = "study_population"

    class Meta:
        ordering = ("id",)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @staticmethod
    def get_qs_json(queryset, json_encode=True):
        outcomes = [outcome.get_json(json_encode=False) for outcome in queryset]
        if json_encode:
            return json.dumps(outcomes, cls=HAWCDjangoJSONEncoder)
        else:
            return outcomes

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    def get_absolute_url(self):
        return reverse("epi:outcome_detail", args=(self.pk,))

    def can_create_sets(self):
        return not self.study_population.can_create_sets()

    @staticmethod
    def flat_complete_header_row():
        return (
            "outcome-id",
            "outcome-url",
            "outcome-name",
            "outcome-effects",
            "outcome-system",
            "outcome-effect",
            "outcome-effect_subtype",
            "outcome-diagnostic",
            "outcome-diagnostic_description",
            "outcome-age_of_measurement",
            "outcome-outcome_n",
            "outcome-summary",
            "outcome-created",
            "outcome-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["url"],
            ser["name"],
            "|".join([str(d["name"]) for d in ser["effects"]]),
            ser["system"],
            ser["effect"],
            ser["effect_subtype"],
            ser["diagnostic"],
            ser["diagnostic_description"],
            ser["age_of_measurement"],
            ser["outcome_n"],
            ser["summary"],
            ser["created"],
            ser["last_updated"],
        )

    def get_study(self):
        return self.study_population.get_study()


class ComparisonSet(models.Model):
    objects = managers.ComparisonSetManager()

    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.SET_NULL, related_name="comparison_sets", null=True
    )
    outcome = models.ForeignKey(
        Outcome, on_delete=models.SET_NULL, related_name="comparison_sets", null=True
    )
    name = models.CharField(
        max_length=256,
        help_text="Name the comparison set, following the format <b>Exposure (If log transformed indicate Ln or Logbase) "
        + "(If continuous, quartiles, tertiles, etc.) (Any other applicable information on analysis) - identifying "
        + "characteristics of exposed group.</b> Each group is a collection of people, and all groups in this collection "
        + "are comparable to one another. You may create a comparison set which contains two groups: cases and controls. "
        + "Alternatively, for cohort-based studies, you may create a comparison set with four different groups, one for "
        + "each quartile of exposure based on exposure measurements. Ex. PFNA (Ln) (Tertiles) - newborn boys"
        + formatHelpTextNotes(
            "Common identifying characteristics: cases, controls, newborns, boys, girls, men, women, pregnant women"
        ),
    )
    exposure = models.ForeignKey(
        "Exposure",
        on_delete=models.SET_NULL,
        related_name="comparison_sets",
        help_text="Which exposure group is associated with this comparison set?",
        blank=True,
        null=True,
    )
    description = models.TextField(
        blank=True,
        help_text="Provide additional comparison set or extraction details if necessary",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def BREADCRUMB_PARENT(self) -> str:
        if self.study_population is not None:
            return "study_population"
        elif self.outcome is not None:
            return "outcome"
        else:
            raise ValueError("Undetermined parent field")

    class Meta:
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not xor(self.outcome is None, self.study_population is None):
            raise ValueError("An outcome or study-population is required.")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("epi:cs_detail", args=(self.pk,))

    def get_assessment(self):
        if self.outcome:
            return self.outcome.get_assessment()
        else:
            return self.study_population.get_assessment()

    def __str__(self):
        return self.name

    @staticmethod
    def flat_complete_header_row():
        return (
            "cs-id",
            "cs-url",
            "cs-name",
            "cs-description",
            "cs-created",
            "cs-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["url"],
            ser["name"],
            ser["description"],
            ser["created"],
            ser["last_updated"],
        )

    def get_study(self):
        if self.study_population:
            return self.study_population.get_study()
        elif self.outcome:
            return self.outcome.get_study()
        else:
            raise ValueError("Study cannot be determined")


class Group(models.Model):
    objects = managers.GroupManager()

    comparison_set = models.ForeignKey(
        ComparisonSet, on_delete=models.CASCADE, related_name="groups"
    )
    group_id = models.PositiveSmallIntegerField()
    name = models.CharField(
        max_length=256,
        help_text='First note "Cases" or "Controls" if applicable, then "Continuous" for continuous exposure '
        + 'or the appropriate quartile/tertile/etc. for categorial ("Q1", "Q2", etc). Ex. Cases Q3; Continuous',
    )
    numeric = models.FloatField(
        verbose_name="Numerical value (sorting)",
        help_text="For categorical, note position in which groups should be listed in visualizations. Ex. Q1: 1"
        + " "
        + HAWC_VIS_NOTE_UNSTYLED,
        blank=True,
        null=True,
    )
    comparative_name = models.CharField(
        max_length=64,
        verbose_name="Comparative Name",
        help_text="Group and value, displayed in plots, for example "
        + '"1.5-2.5(Q2) vs ≤1.5(Q1)", or if only one group is '
        + 'available, "4.8±0.2 (mean±SEM)". For categorical, eg., referent; Q2 vs. Q1 '
        + 'The referent group against which exposure or "index" groups are compared is '
        + "typically the group with the lowest or no exposure",
        blank=True,
    )
    sex = models.CharField(max_length=1, default=constants.Sex.U, choices=constants.Sex.choices)
    ethnicities = models.ManyToManyField(Ethnicity, blank=True, help_text="Optional")
    eligible_n = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Eligible N", help_text="Optional"
    )
    invited_n = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Invited N", help_text="Optional"
    )
    participant_n = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Participant N", help_text="Ex. 1400"
    )
    isControl = models.BooleanField(
        verbose_name="Control?",
        default=None,
        choices=constants.IS_CONTROL_CHOICES,
        help_text="Should this group be interpreted as a null/control group, if applicable",
        null=True,
        blank=True,
    )
    comments = models.TextField(
        blank=True,
        help_text="Provide additional group or extraction details if necessary",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "comparison_set"

    class Meta:
        ordering = (
            "comparison_set",
            "group_id",
        )

    def get_absolute_url(self):
        return reverse("epi:g_detail", args=(self.pk,))

    def get_assessment(self):
        return self.comparison_set.get_assessment()

    def __str__(self):
        return self.name

    @staticmethod
    def flat_complete_header_row():
        return (
            "group-id",
            "group-group_id",
            "group-name",
            "group-numeric",
            "group-comparative_name",
            "group-sex",
            "group-ethnicities",
            "group-eligible_n",
            "group-invited_n",
            "group-participant_n",
            "group-isControl",
            "group-comments",
            "group-created",
            "group-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["group_id"],
            ser["name"],
            ser["numeric"],
            ser["comparative_name"],
            ser["sex"],
            "|".join([d["name"] for d in ser["ethnicities"]]),
            ser["eligible_n"],
            ser["invited_n"],
            ser["participant_n"],
            ser["isControl"],
            ser["comments"],
            ser["created"],
            ser["last_updated"],
        )


class Exposure(models.Model):
    objects = managers.ExposureManager()

    ROUTE_HELP_TEXT = "Select the most significant route(s) of chemical exposure"

    TEXT_CLEANUP_FIELDS = (
        "metric_description",
        "analytical_method",
    )

    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposures"
    )
    name = models.CharField(
        max_length=128,
        help_text="Name of chemical exposure; use abbreviation. Ex. PFNA; DEHP",
    )
    dtxsid = models.ForeignKey(
        DSSTox,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="DSSTox substance identifier (DTXSID)",
        related_name="exposures",
        help_text=DSSTox.help_text(),
    )

    # for help_text for these fields, see ROUTE_HELP_TEXT
    inhalation = models.BooleanField(default=False)
    dermal = models.BooleanField(default=False)
    oral = models.BooleanField(default=False)
    in_utero = models.BooleanField(default=False)
    iv = models.BooleanField(default=False, verbose_name="Intravenous (IV)")
    unknown_route = models.BooleanField(default=False)

    measured = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="What was measured",
        help_text="Chemical measured in study; typically, the same as chemical exposure, but occasionally "
        + "chemical exposure metabolite or another chemical signal. Use abbreviation. Ex PFNA; MEHP",
    )
    metric = models.CharField(
        max_length=128,
        verbose_name="Measurement metric",
        help_text="In what was the chemical measured? Ex. Air; Maternal serum"
        + formatHelpTextNotes(
            "Exposure medium (ex. air, water), tissue or bodily fluid in which biomarker "
            + "detected (ex. blood, serum, plasma, urine, feces, breast milk, hair, saliva, teeth, finger or "
            + "toe nails), or occupation from which exposure assumed (cadmium factory worker)"
        )
        + HAWC_VIS_NOTE,
    )
    metric_units = models.ForeignKey(
        "assessment.DoseUnits",
        on_delete=models.CASCADE,
        help_text="Note chemical measurement units (metric system); if no units given, that is, chemical exposure assumed "
        + "from occupation or survey data, note appropriate exposure categories. Ex. ng/mL; Y/N; electroplating/welding/other"
        + HAWC_VIS_NOTE,
    )
    metric_description = models.TextField(
        verbose_name="Measurement description",
        help_text="Briefly describe how chemical levels in measurement metric were assessed. Ex. Single plasma sample collected for "
        + "each pregnant woman during the first trimester"
        + formatHelpTextNotes(
            "Note key details or if measurement details not provided. May vary by assessment."
        ),
    )
    analytical_method = models.TextField(
        help_text="Lab technique and related information (such as system, corporation name and location) used to measure "
        + 'chemical exposure levels. Ex. "Three PFAS (PFOA, PFOS, and PFHxS) were measured in first-trimester plasma using ultra-high-pressure '
        + "liquid chromatography (ACQUITY UPLC System; Waters Corporation, Milford, Massachusetts) coupled with tandem mass spectrometry, "
        + 'operated in the multiple reaction monitoring mode with an electrospray ion source in negative mode."'
    )
    sampling_period = models.CharField(
        max_length=128, help_text="Exposure sampling period" + OPTIONAL_NOTE, blank=True
    )
    age_of_exposure = models.CharField(
        max_length=32,
        blank=True,
        help_text="When exposure measurement sample was taken, treatment given, and/or specific age or range of ages for which "
        + "survey data apply; quantitative information (mean, median, SE, range) in parentheses where available.  Ex. Pregnancy "
        + "(mean 31 years; SD 4 years); Newborn; Adulthood"
        + formatHelpTextNotes(
            'Use age categories "Fetal" (in utero), "Newborn" (at birth), '
            + '"Neonatal" (0-4 weeks), "Infancy" (0-12 months), "Childhood" (0-11 years), "Adolescence" (12-18 years), '
            + '"Adulthood" (>18 years); may be assessment specific'
        )
        + formatHelpTextNotes(
            'Note "Pregnancy" instead of "Adolescence" or "Adulthood" if applicable'
        )
        + formatHelpTextNotes("If multiple, separate with semicolons")
        + formatHelpTextNotes("Add units for quantitative measurements (days, months, years)"),
    )
    duration = models.CharField(
        max_length=128,
        blank=True,
        help_text="Note exposure duration<br/>"
        + "Ex. Acute, Short-term (2 weeks), Chronic, Developmental, Unclear."
        + formatHelpTextNotes(
            "In many cases (e.g. most cross-sectional studies) exposure duration will be difficult "
            + "to establish; use “Unclear” if duration cannot be empirically derived from study design"
        ),
    )
    exposure_distribution = models.CharField(
        max_length=128,
        blank=True,
        help_text="Enter exposure distribution details not noted in fields below. Ex. 25th percentile=1.18; 75th percentile=3.33"
        + formatHelpTextNotes(
            "Typically 25th and 75th percentiles or alternative central tendency estimate"
        ),
    )
    n = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=OPTIONAL_NOTE
        + "<span class='optional'>Number of individuals where exposure was measured</span>",
    )
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study_population"

    class Meta:
        ordering = ("name",)
        verbose_name = "Exposure"
        verbose_name_plural = "Exposures"

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.study_population.get_assessment()

    def get_absolute_url(self):
        return reverse("epi:exp_detail", args=(self.pk,))

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @staticmethod
    def flat_complete_header_row():
        return (
            "exposure-id",
            "exposure-url",
            "exposure-name",
            "exposure-inhalation",
            "exposure-dermal",
            "exposure-oral",
            "exposure-in_utero",
            "exposure-iv",
            "exposure-unknown_route",
            "exposure-measured",
            "exposure-metric",
            "exposure-metric_units_id",
            "exposure-metric_units_name",
            "exposure-metric_description",
            "exposure-analytical_method",
            "exposure-sampling_period",
            "exposure-age_of_exposure",
            "exposure-duration",
            "exposure-n",
            "exposure-exposure_distribution",
            "exposure-description",
            "exposure-created",
            "exposure-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        if ser is None:
            ser = {}
        units = ser.get("metric_units", {})
        return (
            ser.get("id"),
            ser.get("url"),
            ser.get("name"),
            ser.get("inhalation"),
            ser.get("dermal"),
            ser.get("oral"),
            ser.get("in_utero"),
            ser.get("iv"),
            ser.get("unknown_route"),
            ser.get("measured"),
            ser.get("metric"),
            units.get("id"),
            units.get("name"),
            ser.get("metric_description"),
            ser.get("analytical_method"),
            ser.get("sampling_period"),
            ser.get("age_of_exposure"),
            ser.get("duration"),
            ser.get("n"),
            ser.get("exposure_distribution"),
            ser.get("description"),
            ser.get("created"),
            ser.get("last_updated"),
        )

    def get_study(self):
        return self.study_population.get_study()


class CentralTendency(models.Model):
    # object = managers.CentralTendencyManager

    exposure = models.ForeignKey(
        Exposure, on_delete=models.CASCADE, related_name="central_tendencies"
    )

    estimate = models.FloatField(
        blank=True,
        null=True,
        help_text="Use the central tendency estimate most commonly reported in the set of studies (typically mean or median). "
        + "Ex. 0.78"
        + formatHelpTextNotes("Note: type and units recorded in other fields")
        + HAWC_VIS_NOTE,
    )
    estimate_type = models.PositiveSmallIntegerField(
        choices=constants.EstimateType.choices,
        verbose_name="Central estimate type",
        default=constants.EstimateType.NONE,
    )
    variance = models.FloatField(blank=True, null=True, verbose_name="Variance")
    variance_type = models.PositiveSmallIntegerField(
        choices=constants.VarianceType.choices, default=constants.VarianceType.NONE
    )
    lower_ci = models.FloatField(
        blank=True, null=True, verbose_name="Lower CI", help_text="Numerical value"
    )
    upper_ci = models.FloatField(
        blank=True, null=True, verbose_name="Upper CI", help_text="Numerical value"
    )
    lower_range = models.FloatField(
        blank=True, null=True, verbose_name="Lower range", help_text="Numerical value"
    )
    upper_range = models.FloatField(
        blank=True, null=True, verbose_name="Upper range", help_text="Numerical value"
    )
    description = models.TextField(
        blank=True,
        help_text="Provide additional exposure or extraction details if necessary",
    )

    @property
    def lower_bound_interval(self):
        return self.lower_range if self.lower_ci is None else self.lower_ci

    @property
    def upper_bound_interval(self):
        return self.upper_range if self.upper_ci is None else self.upper_ci

    class Meta:
        ordering = ("estimate_type",)
        verbose_name = "Central Tendency"
        verbose_name_plural = "Central Tendencies"

    def __str__(self):
        return f"{{CT id={self.id}, exposure={self.exposure}}}"

    @staticmethod
    def flat_complete_header_row():
        return (
            "central_tendency-id",
            "central_tendency-estimate",
            "central_tendency-estimate_type",
            "central_tendency-variance",
            "central_tendency-variance_type",
            "central_tendency-lower_ci",
            "central_tendency-upper_ci",
            "central_tendency-lower_range",
            "central_tendency-upper_range",
            "central_tendency-description",
            "central_tendency-lower_bound_interval",
            "central_tendency-upper_bound_interval",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        if ser is None:
            ser = {}
        return (
            ser.get("id"),
            ser.get("estimate"),
            ser.get("estimate_type"),
            ser.get("variance"),
            ser.get("variance_type"),
            ser.get("lower_ci"),
            ser.get("upper_ci"),
            ser.get("lower_range"),
            ser.get("upper_range"),
            ser.get("description"),
            ser.get("lower_bound_interval"),
            ser.get("upper_bound_interval"),
        )


class GroupNumericalDescriptions(models.Model):
    objects = managers.GroupNumericalDescriptionsManager()

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="descriptions")
    description = models.CharField(
        max_length=128,
        help_text="Description if numeric ages do not make sense for this "
        "study-population (ex: longitudinal studies)",
    )
    mean = models.FloatField(blank=True, null=True, verbose_name="Central estimate")
    mean_type = models.PositiveSmallIntegerField(
        choices=constants.GroupMeanType.choices,
        verbose_name="Central estimate type",
        default=constants.GroupMeanType.NONE,
    )
    is_calculated = models.BooleanField(
        default=False, help_text="Was value calculated/estimated from literature?"
    )
    variance = models.FloatField(blank=True, null=True)
    variance_type = models.PositiveSmallIntegerField(
        choices=constants.GroupVarianceType.choices, default=constants.GroupVarianceType.NONE
    )
    lower = models.FloatField(blank=True, null=True)
    lower_type = models.PositiveSmallIntegerField(
        choices=constants.LowerLimit.choices, default=constants.LowerLimit.NONE
    )
    upper = models.FloatField(blank=True, null=True)
    upper_type = models.PositiveSmallIntegerField(
        choices=constants.UpperLimit.choices, default=constants.UpperLimit.NONE
    )

    class Meta:
        verbose_name_plural = "Group Numerical Descriptions"

    def __str__(self):
        return self.description

    def get_assessment(self):
        return self.group.get_assessment()

    def get_absolute_url(self):
        return self.group.get_absolute_url()


class ResultMetric(models.Model):
    objects = managers.ResultMetricManager()

    metric = models.CharField(max_length=128, unique=True)
    abbreviation = models.CharField(max_length=32)
    isLog = models.BooleanField(
        default=True,
        verbose_name="Display as log",
        help_text="When plotting, use a log base 10 scale",
    )
    showForestPlot = models.BooleanField(
        default=True,
        verbose_name="Show on forest plot",
        help_text="Does forest-plot representation of result make sense?",
    )
    reference_value = models.FloatField(
        help_text="Null hypothesis value for reference, if applicable",
        default=1,
        blank=True,
        null=True,
    )
    order = models.PositiveSmallIntegerField(help_text="Order as they appear in option-list")

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.metric


class ResultAdjustmentFactor(models.Model):
    objects = managers.ResultAdjustmentFactorManager()

    adjustment_factor = models.ForeignKey(
        "AdjustmentFactor", on_delete=models.CASCADE, related_name="resfactors"
    )
    result = models.ForeignKey("Result", on_delete=models.CASCADE, related_name="resfactors")
    included_in_final_model = models.BooleanField(default=True)


class Result(models.Model):
    objects = managers.ResultManager()

    name = models.CharField(
        max_length=256,
        help_text="Name the result, following the format <b>Effect Exposure (If log-transformed) (continuous, quartiles, tertiles, etc.) "
        + "- subgroup</b>. Ex. Hyperthyroidism PFHxS (ln) (continuous) - women"
        + HAWC_VIS_NOTE,
    )
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, related_name="results")
    comparison_set = models.ForeignKey(
        ComparisonSet, on_delete=models.CASCADE, related_name="results"
    )
    metric = models.ForeignKey(
        ResultMetric,
        on_delete=models.CASCADE,
        related_name="results",
        help_text="Select the most specific term for the result metric",
    )
    metric_description = models.TextField(
        blank=True,
        help_text='Specify metric if "other"; optionally, provide details. Ex. Bayesian hierarchical linear regression estimates (betas) and 95% CI between quartile increases in maternal plasma PFAS concentrations (ug/L) and ponderal index (kg/m^3)',
    )
    metric_units = models.TextField(
        blank=True,
        help_text="Note Units: Ex. IQR increase, unit (ng/mL) increase, ln-unit (ng/mL) increase",
    )
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature. Ex. Figure 1; Supplemental Table 2",
    )
    population_description = models.CharField(
        max_length=128,
        help_text="Describe the population subset studied for this outcome, following the format "
        + "<b>Male or female adults or children (n)</b>. Ex. Women (n=1200); Newborn girls (n=33)"
        + HAWC_VIS_NOTE,
        blank=True,
    )
    dose_response = models.PositiveSmallIntegerField(
        verbose_name="Dose Response Trend",
        help_text=OPTIONAL_NOTE,
        default=constants.DoseResponse.NA,
        choices=constants.DoseResponse.choices,
    )
    dose_response_details = models.TextField(blank=True, help_text=OPTIONAL_NOTE)
    prevalence_incidence = models.CharField(
        max_length=128,
        verbose_name="Overall incidence prevalence",
        help_text=OPTIONAL_NOTE,
        blank=True,
    )
    statistical_power = models.PositiveSmallIntegerField(
        help_text="Is the study sufficiently powered?" + OPTIONAL_NOTE,
        default=constants.StatisticalPower.NR,
        choices=constants.StatisticalPower.choices,
    )
    statistical_power_details = models.TextField(blank=True, help_text=OPTIONAL_NOTE)
    statistical_test_results = models.TextField(blank=True, help_text=OPTIONAL_NOTE)
    trend_test = models.CharField(
        verbose_name="Trend test result",
        max_length=128,
        blank=True,
        help_text=OPTIONAL_NOTE
        + "<span class='optional'>Enter result, if available (ex: p=0.015, p≤0.05, n.s., etc.)</span>",
    )
    adjustment_factors = models.ManyToManyField(
        AdjustmentFactor,
        through=ResultAdjustmentFactor,
        related_name="outcomes",
        blank=True,
    )
    estimate_type = models.PositiveSmallIntegerField(
        choices=constants.EstimateType.choices,
        verbose_name="Central estimate type",
        default=constants.EstimateType.NONE,
    )
    variance_type = models.PositiveSmallIntegerField(
        choices=constants.VarianceType.choices, default=constants.VarianceType.NONE
    )
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name="Confidence interval (CI)",
        help_text="Write as a decimal: a 95% CI should be recorded as 0.95. Ex. 0.95",
    )
    comments = models.TextField(
        blank=True,
        help_text="Summarize main findings (optional) or describe why no details are presented. Ex. No association (data not shown)",
    )

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    resulttags = models.ManyToManyField(EffectTag, blank=True, verbose_name="Tags")

    BREADCRUMB_PARENT = "outcome"

    class Meta:
        ordering = ("id",)

    @property
    def factors_applied(self):
        return self.adjustment_factors.filter(resfactors__included_in_final_model=True)

    @property
    def factors_considered(self):
        return self.adjustment_factors.filter(resfactors__included_in_final_model=False)

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.outcome.get_assessment()

    def get_absolute_url(self):
        return reverse("epi:result_detail", args=(self.pk,))

    @staticmethod
    def flat_complete_header_row():
        return (
            "metric-id",
            "metric-name",
            "metric-abbreviation",
            "result-id",
            "result-name",
            "result-metric_description",
            "result-metric_units",
            "result-data_location",
            "result-population_description",
            "result-dose_response",
            "result-dose_response_details",
            "result-prevalence_incidence",
            "result-statistical_power",
            "result-statistical_power_details",
            "result-statistical_test_results",
            "result-trend_test",
            "result-adjustment_factors",
            "result-adjustment_factors_considered",
            "result-estimate_type",
            "result-variance_type",
            "result-ci_units",
            "result-comments",
            "result-created",
            "result-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        def getFactorList(lst, isIncluded):
            return "|".join(
                [
                    d["description"]
                    for d in [d for d in lst if d["included_in_final_model"] == isIncluded]
                ]
            )

        return (
            ser["metric"]["id"],
            ser["metric"]["metric"],
            ser["metric"]["abbreviation"],
            ser["id"],
            ser["name"],
            ser["metric_description"],
            ser["metric_units"],
            ser["data_location"],
            ser["population_description"],
            ser["dose_response"],
            ser["dose_response_details"],
            ser["prevalence_incidence"],
            ser["statistical_power"],
            ser["statistical_power_details"],
            ser["statistical_test_results"],
            ser["trend_test"],
            getFactorList(ser["factors"], True),
            getFactorList(ser["factors"], False),
            ser["estimate_type"],
            ser["variance_type"],
            ser["ci_units"],
            ser["comments"],
            ser["created"],
            ser["last_updated"],
        )

    def get_study(self):
        return self.outcome.get_study()

    @classmethod
    def heatmap_study_df(cls, assessment_id: int, published_only: bool) -> pd.DataFrame:
        def unique_items(els):
            return "|".join(sorted(set(el for el in els if el is not None)))

        def unique_list_items(rows):
            items = set(itertools.chain.from_iterable(row.split("|") for row in rows.unique()))
            return "|".join(sorted(items))

        # get all studies,even if no endpoint data is extracted
        filters: dict[str, Any] = {"assessment_id": assessment_id, "epi": True}
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
            "study design": unique_items,
            "study population source": unique_items,
            "exposure name": unique_items,
            "exposure route": unique_list_items,
            "exposure measure": unique_list_items,
            "exposure metric": unique_list_items,
            "system": unique_items,
            "effect": unique_items,
            "effect subtype": unique_items,
        }
        if "overall study evaluation" in df2:
            aggregates["overall study evaluation"] = unique_items
        df2 = df2.groupby("study id").agg(aggregates)

        # merge all the data frames together
        df = df1.merge(df2, how="left", left_index=True, right_index=True).fillna("").reset_index()
        return df

    @classmethod
    def heatmap_df(cls, assessment_id: int, published_only: bool) -> pd.DataFrame:
        filters = {"outcome__assessment": assessment_id}
        if published_only:
            filters["outcome__study_population__study__published"] = True
        columns = {
            "outcome__study_population__study_id": "study id",
            "outcome__study_population__study__short_citation": "study citation",
            "outcome__study_population__study__study_identifier": "study identifier",
            "outcome__study_population_id": "study population id",
            "outcome__study_population__name": "study population name",
            "outcome__study_population__source": "study population source",
            "outcome__study_population__design": "study design",
            "comparison_set_id": "comparison set id",
            "comparison_set__name": "comparison set name",
            "comparison_set__exposure_id": "exposure id",
            "comparison_set__exposure__name": "exposure name",
            "comparison_set__exposure__measured": "exposure measure",
            "comparison_set__exposure__metric": "exposure metric",
            "outcome_id": "outcome id",
            "outcome__name": "outcome name",
            "outcome__system": "system",
            "outcome__effect": "effect",
            "outcome__effect_subtype": "effect subtype",
            "id": "result id",
            "name": "result name",
        }
        qs = (
            cls.objects.select_related(
                "outcome",
                "comparison_set",
                "comparison_set__exposure",
                "outcome__study_population",
                "outcome__study_population__study",
            )
            .filter(**filters)
            .values_list(*columns.keys())
            .order_by("id")
        )

        df1 = pd.DataFrame(data=list(qs), columns=columns.values())
        df1["study design"] = df1["study design"].map(dict(constants.Design.choices))

        # add exposure column
        exposure_cols = ["inhalation", "dermal", "oral", "in_utero", "iv", "unknown_route"]
        qs = Exposure.objects.filter(study_population__study__assessment=assessment_id).values(
            "id", *exposure_cols
        )

        df2 = pd.DataFrame(data=qs, columns=["id", *exposure_cols]).set_index("id")
        df2["exposure route"] = df2[exposure_cols].apply(
            lambda x: "|".join(x.index[x == True]).replace("_", " "),  # noqa: E712
            axis=1,
        )
        df2 = df2.drop(columns=exposure_cols)

        # join data together
        df = df1.merge(df2, how="left", left_on="exposure id", right_index=True).pipe(
            df_move_column, "exposure route", "exposure name"
        )
        df["exposure route"].fillna("", inplace=True)
        df["exposure measure"].fillna("", inplace=True)
        df["exposure metric"].fillna("", inplace=True)

        # overall risk of bias evaluation
        FinalRiskOfBiasScore = apps.get_model("materialized", "FinalRiskOfBiasScore")
        df2 = FinalRiskOfBiasScore.objects.overall_result_scores(assessment_id)
        if df2 is not None:
            df = (
                df.merge(df2, how="left", left_on="result id", right_on="result id")
                .pipe(df_move_column, "overall study evaluation", "study identifier")
                .fillna("")
            )

        return df


class GroupResult(models.Model):
    objects = managers.GroupResultManager()

    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="results")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="results")
    n = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Individuals in group where outcome was measured." + HAWC_VIS_NOTE_UNSTYLED,
    )
    estimate = models.FloatField(
        blank=True,
        null=True,
        help_text="Central tendency estimate for group." + HAWC_VIS_NOTE_UNSTYLED,
    )
    variance = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Variance",
        help_text="Variance estimate for group, when available." + HAWC_VIS_NOTE_UNSTYLED,
    )
    lower_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Lower CI",
        help_text="Numerical value for lower-confidence interval, when available."
        + HAWC_VIS_NOTE_UNSTYLED,
    )
    upper_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Upper CI",
        help_text="Numerical value for upper-confidence interval, when available."
        + HAWC_VIS_NOTE_UNSTYLED,
    )
    lower_range = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Lower range",
        help_text="Numerical value for lower range, when available." + HAWC_VIS_NOTE_UNSTYLED,
    )
    upper_range = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Upper range",
        help_text="Numerical value for upper range, when available." + HAWC_VIS_NOTE_UNSTYLED,
    )
    p_value_qualifier = models.CharField(
        max_length=1,
        choices=constants.PValueQualifier.choices,
        default="-",
        verbose_name="p-value qualifier",
        help_text="Select n.s. if results are not statistically significant; otherwise, choose the appropriate qualifier. "
        + HAWC_VIS_NOTE_UNSTYLED,
    )
    p_value = models.FloatField(
        blank=True,
        null=True,
        verbose_name="p-value",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Note p-value when available. " + HAWC_VIS_NOTE_UNSTYLED,
    )
    is_main_finding = models.BooleanField(
        default=False,
        verbose_name="Main finding",
        help_text="If study does not report a statistically significant association (p<0.05) between exposure "
        + 'and health outcome at any exposure level, check "Main finding" for highest exposure group '
        + "compared with referent group (e.g.Q4 vs. Q1). If study reports a statistically significant "
        + 'association and monotonic dose response, check "Main finding" for lowest exposure group with '
        + "a statistically significant association. If nonmonotonic dose response, case-by-case considering "
        + "statistical trend analyses, consistency of pattern across exposure groups, and/or biological "
        + 'significance.  See "Results" section of https://ehp.niehs.nih.gov/1205502/ for examples and '
        + "further details. "
        + HAWC_VIS_NOTE_UNSTYLED,
    )
    main_finding_support = models.PositiveSmallIntegerField(
        choices=constants.MainFinding.choices,
        help_text="Select appropriate level of support for the main finding."
        + 'See "Results" section of https://ehp.niehs.nih.gov/1205502/ for examples and further details. '
        + 'Choose between "inconclusive" vs. "not-supportive" based on chemical- and study-specific context. '
        + HAWC_VIS_NOTE_UNSTYLED,
        default=constants.MainFinding.I,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("result", "group__group_id")

    @property
    def p_value_text(self):
        txt = self.get_p_value_qualifier_display()
        if self.p_value is not None:
            if txt in ["=", "-", "n.s."]:
                txt = f"{self.p_value:g}"
            else:
                txt = f"{txt}{self.p_value:g}"

        return txt

    @property
    def lower_bound_interval(self):
        return self.lower_range if self.lower_ci is None else self.lower_ci

    @property
    def upper_bound_interval(self):
        return self.upper_range if self.upper_ci is None else self.upper_ci

    @staticmethod
    def flat_complete_header_row():
        return (
            "result_group-id",
            "result_group-n",
            "result_group-estimate",
            "result_group-variance",
            "result_group-lower_ci",
            "result_group-upper_ci",
            "result_group-lower_range",
            "result_group-upper_range",
            "result_group-lower_bound_interval",
            "result_group-upper_bound_interval",
            "result_group-p_value_qualifier",
            "result_group-p_value",
            "result_group-is_main_finding",
            "result_group-main_finding_support",
            "result_group-created",
            "result_group-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["n"],
            ser["estimate"],
            ser["variance"],
            ser["lower_ci"],
            ser["upper_ci"],
            ser["lower_range"],
            ser["upper_range"],
            ser["lower_bound_interval"],
            ser["upper_bound_interval"],
            ser["p_value_qualifier_display"],
            ser["p_value"],
            ser["is_main_finding"],
            ser["main_finding_support"],
            ser["created"],
            ser["last_updated"],
        )

    @staticmethod
    def stdev(variance_type, variance, n):
        # calculate stdev given re
        if variance_type == "SD":
            return variance
        elif variance_type in ["SE", "SEM"] and variance is not None and n is not None:
            return variance * math.sqrt(n)
        else:
            return None

    @classmethod
    def getStdevs(cls, variance_type, rgs):
        for rg in rgs:
            rg["stdev"] = cls.stdev(variance_type, rg["variance"], rg["n"])

    @staticmethod
    def getConfidenceIntervals(variance_type, groups):
        """
        Expects a dictionary of endpoint groups and the endpoint variance-type.
        Appends results to the dictionary for each endpoint-group.

        Confidence interval calculated using a two-tailed t-test,
        assuming 95% confidence interval.
        """

        for grp in groups:
            lower_ci = grp.get("lower_ci")
            upper_ci = grp.get("upper_ci")
            n = grp.get("n")
            if (
                lower_ci is None
                and upper_ci is None
                and n is not None
                and grp["lower_range"] is None
                and grp["upper_range"] is None
                and grp["estimate"] is not None
                and grp["variance"] is not None
            ):
                est = grp["estimate"]
                var = grp["variance"]
                z = t.ppf(0.975, max(n - 1, 1))
                change = None

                if variance_type == "SD":
                    change = z * var / math.sqrt(n)
                elif variance_type in ("SE", "SEM"):
                    change = z * var

                if change is not None:
                    lower_ci = round(est - change, 2)
                    upper_ci = round(est + change, 2)

                grp.update(lower_ci=lower_ci, upper_ci=upper_ci, ci_calc=True)

    @staticmethod
    def percentControl(estimate_type, variance_type, rgs):
        """
        Expects a dictionary of result groups, the result estimate_type, and
        result variance_type. Appends results to the dictionary for each result-group.

        Calculates a 95% confidence interval for the percent-difference from
        control, taking into account variance from both groups using a
        Fisher Information Matrix, assuming independent normal distributions.

        Only calculates if estimate_type is 'median' or 'mean' and variance_type
        is 'SD', 'SE', or 'SEM', all cases are true with a normal distribution.
        """

        def get_control_group(rgs):
            """
            - If 0 groups are control=true, the first group will be chosen as control
            - If 1 group is control=true, it will be used as control
            - If ≥2 groups is control=true, a random control group will be chosen as control
            """
            control = None

            for i, rg in enumerate(rgs):
                if rg["group"]["isControl"]:
                    control = rg
                    break

            if control is None:
                control = rgs[0]

            return control["n"], control["estimate"], control.get("stdev")

        if len(rgs) == 0:
            return

        n_1, mu_1, sd_1 = get_control_group(rgs)

        for i, rg in enumerate(rgs):
            mean = low = high = None

            if estimate_type in ["median", "mean"] and variance_type in [
                "SD",
                "SE",
                "SEM",
            ]:
                n_2 = rg["n"]
                mu_2 = rg["estimate"]
                sd_2 = rg.get("stdev")

                if mu_1 and mu_2 and mu_1 != 0:
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

            rg.update(percentControlMean=mean, percentControlLow=low, percentControlHigh=high)

    def get_assessment(self):
        return self.result.get_assessment()


reversion.register(Country)
reversion.register(Criteria)
reversion.register(Ethnicity)
reversion.register(StudyPopulationCriteria)
reversion.register(AdjustmentFactor)
reversion.register(ResultAdjustmentFactor)
reversion.register(StudyPopulation, follow=("countries", "spcriteria"))
reversion.register(ComparisonSet)
reversion.register(Exposure)
reversion.register(Outcome, follow=("effects",))
reversion.register(Group, follow=("ethnicities",))
reversion.register(Result, follow=("adjustment_factors", "resfactors", "results"))
reversion.register(GroupResult)
