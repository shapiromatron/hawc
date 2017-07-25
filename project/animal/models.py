#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import json
import math

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist

from reversion import revisions as reversion
from scipy import stats

from assessment.models import Assessment, BaseEndpoint, get_cas_url
from assessment.serializers import AssessmentSerializer
from study.models import Study
from utils.helper import HAWCDjangoJSONEncoder, SerializerHelper, \
    cleanHTML, tryParseInt
from utils.models import get_crumbs

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
        ("Dv", "Developmental"),
        ("Ot", "Other"),
        ("NR", "Not-reported"))

    LITTER_EFFECT_CHOICES = (
        ("NA", "Not-applicable"),
        ("NR", "Not-reported"),
        ("YS", "Yes, statistical controls"),
        ("YD", "Yes, study-design"),
        ("N",  "No"),
        ("O",  "Other"))

    PURITY_QUALIFIER_CHOICES = (
        ('>', '>'),
        ('≥', '≥'),
        ('=', '='),
        ('',  ''))

    TEXT_CLEANUP_FIELDS = (
        'name',
        'chemical',
        'cas',
        'chemical_source',
        'vehicle',
    )

    study = models.ForeignKey(
        'study.Study',
        related_name='experiments')
    name = models.CharField(
        max_length=80,
        help_text="Short-text used to describe the experiment "
                  "(i.e. 2-year cancer bioassay, 28-day inhalation, etc.).")
    type = models.CharField(
        max_length=2,
        choices=EXPERIMENT_TYPE_CHOICES,
        help_text="Type of study being performed; be as specific as-possible")
    chemical = models.CharField(
        max_length=128,
        verbose_name="Chemical name",
        blank=True)
    cas = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Chemical identifier (CAS)",
        help_text="CAS number for chemical-tested, if available.")
    chemical_source = models.CharField(
        max_length=128,
        verbose_name="Source of chemical",
        blank=True)
    purity_available = models.BooleanField(
        default=True,
        verbose_name="Chemical purity available?")
    purity_qualifier = models.CharField(
        max_length=1,
        choices=PURITY_QUALIFIER_CHOICES,
        blank=True,
        default='')
    purity = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Chemical purity (%)",
        help_text="Percentage (ex: 95%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    vehicle = models.CharField(
        max_length=64,
        verbose_name="Chemical vehicle",
        help_text="If a vehicle was used, vehicle common-name",
        blank=True)
    diet = models.TextField(
        help_text="Description of animal-feed, if relevant",
        blank=True)
    guideline_compliance = models.CharField(
        max_length=128,
        blank=True,
        help_text="""Description of any compliance methods used (i.e. use of EPA
            OECD, NTP, or other guidelines; conducted under GLP guideline
            conditions, non-GLP but consistent with guideline study, etc.)""")
    litter_effects = models.CharField(
        max_length=2,
        choices=LITTER_EFFECT_CHOICES,
        default="NA",
        help_text="Type of controls used for litter-effects")
    litter_effect_notes = models.CharField(
        max_length=128,
        help_text="Any additional notes describing how litter effects were controlled",
        blank=True)
    description = models.TextField(
        blank=True,
        verbose_name="Description and animal husbandry",
        help_text="Text-description of the experimental protocol used. "
                  "May also include information such as animal husbandry. "
                  "Note that dosing-regime information and animal details are "
                  "captured in other fields.")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    COPY_NAME = 'experiments'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('animal:experiment_detail', args=[str(self.pk)])

    def is_generational(self):
        return self.type in ["Rp", "Dv"]

    def get_assessment(self):
        return self.study.get_assessment()

    def get_crumbs(self):
        return get_crumbs(self, self.study)

    @property
    def cas_url(self):
        return get_cas_url(self.cas)

    @staticmethod
    def flat_complete_header_row():
        return (
            'experiment-id',
            'experiment-url',
            'experiment-name',
            'experiment-type',
            'experiment-chemical',
            'experiment-cas',
            'experiment-chemical_source',
            'experiment-purity_available',
            'experiment-purity_qualifier',
            'experiment-purity',
            'experiment-vehicle',
            'experiment-diet',
            'experiment-litter_effects',
            'experiment-litter_effect_notes',
            'experiment-guideline_compliance',
            'experiment-description'
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            ser['type'],
            ser['chemical'],
            ser['cas'],
            ser['chemical_source'],
            ser['purity_available'],
            ser['purity_qualifier'],
            ser['purity'],
            ser['vehicle'],
            ser['diet'],
            ser['litter_effects'],
            ser['litter_effect_notes'],
            ser['guideline_compliance'],
            cleanHTML(ser['description'])
        )

    @classmethod
    def delete_caches(cls, ids):
        Endpoint.delete_caches(
            Endpoint.objects
                .filter(animal_group__experiment__in=ids)
                .values_list('id', flat=True)
        )

    def copy_across_assessments(self, cw):
        children = list(self.animal_groups.all())
        old_id = self.id
        self.id = None
        self.study_id = cw[Study.COPY_NAME][self.study_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        cw[AnimalGroup.COPY_NAME]['parents'] = collections.defaultdict(list)
        for child in children:
            child.copy_across_assessments(cw)
        for child in self.animal_groups.all():
            child.complete_copy(cw)


class AnimalGroup(models.Model):
    objects = managers.AnimalGroupManager()

    SEX_SYMBOLS = {
        "M": "♂",
        "F": "♀",
        "C": "♂♀",
        "R": "NR"
    }

    SEX_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("C", "Combined"),
        ("R", "Not reported"))

    GENERATION_CHOICES = (
        (""  , "N/A (not generational-study)"),
        ("P0", "Parent-generation (P0)"),
        ("F1", "First-generation (F1)"),
        ("F2", "Second-generation (F2)"),
        ("F3", "Third-generation (F3)"),
        ("F4", "Fourth-generation (F4)"),
        ("Ot", "Other"))

    TEXT_CLEANUP_FIELDS = (
        'name',
        'animal_source',
        'lifestage_exposed',
        'lifestage_assessed',
    )

    experiment = models.ForeignKey(
        Experiment,
        related_name="animal_groups")
    name = models.CharField(
        max_length=80,
        help_text="Short description of the animals (i.e. Male Fischer F344 rats, Female C57BL/6 mice)"
        )
    species = models.ForeignKey(
        'assessment.Species')
    strain = models.ForeignKey(
        'assessment.Strain')
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES)
    animal_source = models.CharField(
        max_length=128,
        help_text="Laboratory and/or breeding details where animals were acquired",
        blank=True)
    lifestage_exposed = models.CharField(
        max_length=32,
        blank=True,
        help_text='Textual life-stage description when exposure occurred '
                  '(examples include: "parental, PND18, juvenile, adult, '
                  'continuous, multiple")')
    lifestage_assessed = models.CharField(
        max_length=32,
        blank=True,
        help_text='Textual life-stage description when endpoints were measured '
                  '(examples include: "parental, PND18, juvenile, adult, multiple")')
    duration_observation = models.FloatField(
        verbose_name="Observation duration (days)",
        help_text="Numeric length of observation period, in days (fractions allowed)",
        blank=True,
        null=True)
    siblings = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    generation = models.CharField(
        blank=True,
        default = "",
        max_length=2,
        choices=GENERATION_CHOICES)
    parents = models.ManyToManyField(
        "self",
        related_name="children",
        symmetrical=False,
        blank=True)
    dosing_regime = models.ForeignKey(
        'DosingRegime',
        help_text='Specify an existing dosing regime or create a new dosing regime below',
        blank=True,
        null=True)  # not enforced in db, but enforced in views
    comments = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Any addition notes for this animal-group.")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    COPY_NAME = 'animal_groups'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('animal:animal_group_detail', args=[str(self.pk)])

    def get_assessment(self):
        return self.experiment.get_assessment()

    def get_crumbs(self):
        return get_crumbs(self, self.experiment)

    @property
    def is_generational(self):
        return self.experiment.is_generational()

    @property
    def sex_symbol(self):
        return self.SEX_SYMBOLS.get(self.sex)

    def get_doses_json(self, json_encode=True):
        if not hasattr(self, 'doses'):
            self.doses = [{"error": "no dosing regime"}]
            self.doses = self.dosing_regime.get_doses_json(False)
        if json_encode:
            return json.dumps(self.doses, cls=HAWCDjangoJSONEncoder)
        return self.doses

    @property
    def generation_short(self):
        return "Other" if self.generation == "Ot" else self.generation

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
            "animal_group-duration_observation",
            "animal_group-siblings",
            "animal_group-parents",
            "animal_group-generation",
            "animal_group-comments",
            "species-name",
            "strain-name",
        )

    @classmethod
    def get_relation_id(cls, rel):
        return str(rel['id']) if rel else None

    @classmethod
    def flat_complete_data_row(cls, ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            ser['sex'],
            ser['animal_source'],
            ser['lifestage_exposed'],
            ser['lifestage_assessed'],
            ser['duration_observation'],
            cls.get_relation_id(ser['siblings']),
            '|'.join([cls.get_relation_id(p) for p in ser['parents']]),
            ser['generation'],
            cleanHTML(ser['comments']),
            ser['species'],
            ser['strain']
        )

    @classmethod
    def delete_caches(cls, ids):
        Endpoint.delete_caches(
            Endpoint.objects
                .filter(animal_group__in=ids)
                .values_list('id', flat=True)
        )

    def copy_across_assessments(self, cw):
        children = list(self.endpoints.all())
        old_id = self.id
        parent_ids = [p.id for p in self.parents.all()]
        self.id = None
        self.experiment_id = cw[Experiment.COPY_NAME][self.experiment_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        cw[self.COPY_NAME]['parents'][self.id] = parent_ids
        for child in children:
            child.copy_across_assessments(cw)

    def complete_copy(self, cw):
        # copy parent animal group over
        for old_parent_id in cw[self.COPY_NAME]['parents'][self.id]:
            parent_id = cw[AnimalGroup.COPY_NAME][old_parent_id]
            self.parents.add(AnimalGroup.objects.get(pk=parent_id))
        # only create dosing_regime if it doesn't exist
        dosing_regime_created = DosingRegime.objects\
            .filter(pk=cw[DosingRegime.COPY_NAME].get(self.dosing_regime_id, None))\
            .exists()
        if not dosing_regime_created:
            self.dosing_regime.copy_across_assessments(cw)
        self.dosing_regime_id = cw[DosingRegime.COPY_NAME][self.dosing_regime_id]
        self.save()


class DosingRegime(models.Model):

    objects = managers.DosingRegimeManager()

    ROUTE_EXPOSURE_CHOICES = (
        ("OR", "Oral"),
        ("OC", "Oral capsule"),
        ("OD", "Oral diet"),
        ("OG", "Oral gavage"),
        ("OW", "Oral drinking water"),
        ("I",  "Inhalation"),
        ("IG", "Inhalation - gas"),
        ("IR", "Inhalation - particle"),
        ("IA", "Inhalation - vapor"),
        ("D",  "Dermal"),
        ("SI", "Subcutaneous injection"),
        ("IP", "Intraperitoneal injection"),
        ("IV", "Intravenous injection"),
        ("IO", "in ovo"),
        ("P",  "Parental"),
        ("W",  "Whole body"),
        ("M",  "Multiple"),
        ("U",  "Unknown"),
        ("O",  "Other"))

    POSITIVE_CONTROL_CHOICES = (
        (True, "Yes"),
        (False, "No"),
        (None, "Unknown"))

    NEGATIVE_CONTROL_CHOICES = (
        ("NR", "Not-reported"),
        ("UN", "Untreated"),
        ("VT", "Vehicle-treated"),
        ("B" , "Untreated + Vehicle-treated"),
        ("Y" , "Yes (untreated and/or vehicle)"),
        ("N" , "No"))

    dosed_animals = models.OneToOneField(
        AnimalGroup,
        related_name='dosed_animals',
        blank=True,
        null=True)
    route_of_exposure = models.CharField(
        max_length=2,
        choices=ROUTE_EXPOSURE_CHOICES,
        help_text="Primary route of exposure. If multiple primary-exposures, describe in notes-field below")
    duration_exposure = models.FloatField(
        verbose_name="Exposure duration (days)",
        help_text="Length of exposure period (fractions allowed), used for sorting in visualizations",
        blank=True,
        null=True)
    duration_exposure_text = models.CharField(
        verbose_name="Exposure duration (text)",
        max_length=128,
        blank=True,
        help_text="Text-description of the exposure duration (ex: 21 days, 104 wks, GD0 to PND9, GD0 to weaning)")
    num_dose_groups = models.PositiveSmallIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        verbose_name="Number of Dose Groups",
        help_text="Number of dose groups, plus control")
    positive_control = models.NullBooleanField(
        choices=POSITIVE_CONTROL_CHOICES,
        default=None,
        help_text="Was a positive control used?")
    negative_control = models.CharField(
        max_length=2,
        default="NR",
        choices=NEGATIVE_CONTROL_CHOICES,
        help_text="Description of negative-controls used")
    description = models.TextField(
        blank=True,
        help_text="Detailed description of dosing methodology (i.e. exposed via inhalation 5 days/week for 6 hours)")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    COPY_NAME = 'dose_regime'

    def __str__(self):
        return '{0} {1}'.format(self.dosed_animals,
                                 self.get_route_of_exposure_display())

    def get_absolute_url(self):
        return self.dosed_animals.get_absolute_url()

    def get_crumbs(self):
        return get_crumbs(self, parent=self.dosed_animals.experiment)

    def get_assessment(self):
        return self.dosed_animals.get_assessment()

    @property
    def dose_groups(self):
        if not hasattr(self, '_dose_groups'):
            self._dose_groups = DoseGroup.objects.select_related('dose_units')\
                                                 .filter(dose_regime=self.pk)
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
            "dosing_regime-num_dose_groups",
            "dosing_regime-positive_control",
            "dosing_regime-negative_control",
            "dosing_regime-description",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            AnimalGroup.get_relation_id(ser['dosed_animals']),
            ser['route_of_exposure'],
            ser['duration_exposure'],
            ser['duration_exposure_text'],
            ser['num_dose_groups'],
            ser['positive_control'],
            ser['negative_control'],
            cleanHTML(ser['description']),
        )

    def get_doses_json(self, json_encode=True):
        doses = []
        dgs = self.dose_groups.order_by('dose_units_id', 'dose_group_id')
        for dg in dgs.distinct('dose_units'):
            dose_values = dgs.filter(dose_units=dg.dose_units)\
                             .values_list('dose', flat=True)
            doses.append({
                'id': dg.dose_units.id,
                'name': dg.dose_units.name,
                'values': list(dose_values)
            })
        if json_encode:
            return json.dumps(doses, cls=HAWCDjangoJSONEncoder)
        else:
            return doses

    def copy_across_assessments(self, cw):
        children = list(self.dose_groups)
        old_id = self.id
        self.id = None
        self.dosed_animals_id = cw[AnimalGroup.COPY_NAME].get(self.dosed_animals_id, None)
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)


class DoseGroup(models.Model):
    objects = managers.DoseGroupManager()

    dose_regime = models.ForeignKey(
        DosingRegime,
        related_name='doses')
    dose_units = models.ForeignKey(
        'assessment.DoseUnits')
    dose_group_id = models.PositiveSmallIntegerField()
    dose = models.FloatField(
        validators=[MinValueValidator(0)])
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    COPY_NAME = 'doses'

    class Meta:
        ordering = ('dose_units', 'dose_group_id')

    def __str__(self):
        return "{0} {1}".format(self.dose, self.dose_units)

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
        'name',
        'system',
        'organ',
        'effect',
        'effect_subtype',
        'observation_time_text',
        'data_location',
        'response_units',
        'statistical_test',
    )

    DATA_TYPE_CHOICES = (
        ('C', 'Continuous'),
        ('D', 'Dichotomous'),
        ('P', 'Percent Difference'),
        ('DC', 'Dichotomous Cancer'),
        ('NR', 'Not reported'))

    MONOTONICITY_CHOICES = (
        (0, "N/A, single dose level study"),
        (1, "N/A, no effects detected"),
        (2, "yes, visual appearance of monotonicity but no trend"),
        (3, "yes, monotonic and significant trend"),
        (4, "yes, visual appearance of non-monotonic but no trend"),
        (5, "yes, non-monotonic and significant trend"),
        (6, "no pattern"),
        (7, "unclear"),
        (8, "not-reported"))

    VARIANCE_TYPE_CHOICES = (
        (0, "NA"),
        (1, "SD"),
        (2, "SE"),
        (3, "NR"))

    VARIANCE_NAME = {
        0: "N/A",
        1: "Standard Deviation",
        2: "Standard Error",
        3: "Not Reported"}

    OBSERVATION_TIME_UNITS = (
        (0, "not-reported"),
        (1, "seconds"),
        (2, "minutes"),
        (3, "hours"),
        (4, "days"),
        (5, "weeks"),
        (6, "months"),
        (9, "years"),
        (7, "PND"),
        (8, "GD"))

    TREND_RESULT_CHOICES = (
        (0, "not applicable"),
        (1, "not significant"),
        (2, "significant"),
        (3, "not reported"))

    ADVERSE_DIRECTION_CHOICES = (
        (3, 'increase from reference/control group'),
        (2, 'decrease from reference/control group'),
        (1, 'any change from reference/control group'),
        (0, 'not reported'),
    )

    animal_group = models.ForeignKey(
        AnimalGroup,
        related_name="endpoints")
    system = models.CharField(
        max_length=128,
        blank=True,
        help_text="Relevant biological system")
    organ = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Organ (and tissue)",
        help_text="Relevant organ; also include tissue if relevant")
    effect = models.CharField(
        max_length=128,
        blank=True,
        help_text="Effect, using common-vocabulary")
    effect_subtype = models.CharField(
        max_length=128,
        blank=True,
        help_text="Effect subtype, using common-vocabulary")
    observation_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Numeric value of the time an observation was reported; "
                  "optional, should be recorded if the same effect was measured multiple times.")
    observation_time_units = models.PositiveSmallIntegerField(
        default=0,
        choices=OBSERVATION_TIME_UNITS)
    observation_time_text = models.CharField(
        max_length=64,
        blank=True,
        help_text='Text for reported observation time (ex: "60-90 PND")')
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
                  "(ex: Figure 1, Table 2, etc.)")
    expected_adversity_direction = models.PositiveSmallIntegerField(
        choices=ADVERSE_DIRECTION_CHOICES,
        default=0,
        verbose_name='Expected response adversity direction',
        help_text='Response direction which would be considered adverse')
    response_units = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Response units",
        help_text="Units the response was measured in (i.e., \u03BCg/dL, % control, etc.)")
    data_type = models.CharField(
        max_length=2,
        choices=DATA_TYPE_CHOICES,
        default="C",
        verbose_name="Dataset type")
    variance_type = models.PositiveSmallIntegerField(
        default=1,
        choices=VARIANCE_TYPE_CHOICES)
    confidence_interval = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Confidence interval (CI)',
        help_text='A 95% CI is written as 0.95.')
    NOEL = models.SmallIntegerField(
        verbose_name="NOEL",
        default=-999,
        help_text="No observed effect level")
    LOEL = models.SmallIntegerField(
        verbose_name="LOEL",
        default=-999,
        help_text="Lowest observed effect level")
    FEL = models.SmallIntegerField(
        verbose_name="FEL",
        default=-999,
        help_text="Frank effect level")
    data_reported = models.BooleanField(
        default=True,
        help_text="Dose-response data for endpoint are available in the literature source")
    data_extracted = models.BooleanField(
        default=True,
        help_text="Dose-response data for endpoint are extracted from literature into HAWC")
    values_estimated = models.BooleanField(
        default=False,
        help_text="Response values were estimated using a digital ruler or other methods")
    monotonicity = models.PositiveSmallIntegerField(
        default=8,
        choices=MONOTONICITY_CHOICES)
    statistical_test = models.CharField(
        max_length=256,
        blank=True,
        help_text="Description of statistical analysis techniques used")
    trend_value = models.FloatField(
        null=True,
        blank=True,
        help_text="Numerical result for trend-test, if available")
    trend_result = models.PositiveSmallIntegerField(
        default=3,
        choices=TREND_RESULT_CHOICES)
    diagnostic = models.TextField(
        blank=True,
        help_text="Diagnostic or method used to measure endpoint (if relevant)")
    power_notes = models.TextField(
        blank=True,
        help_text="Power of study-design to detect change from control")
    results_notes = models.TextField(
        blank=True,
        help_text="Qualitative description of the results")
    endpoint_notes = models.TextField(
        blank=True,
        verbose_name="General notes/methodology",
        help_text="Any additional notes related to this endpoint/methodology, not including results")
    additional_fields = models.TextField(
        default="{}")

    COPY_NAME = 'endpoints'

    def get_update_url(self):
        return reverse('animal:endpoint_update', args=[self.pk])

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('animal:endpoint_detail', args=[str(self.pk)])

    def get_crumbs(self):
        return get_crumbs(self, self.animal_group)

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
        if not hasattr(self, 'doses'):
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
        qs = queryset\
            .annotate(max_egs=models.Count('groups', distinct=True))\
            .values_list('max_egs', flat=True)
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
        resps = self.groups.values_list('response', flat=True)
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
            ser['id'],
            ser['url'],
            ser['name'],
            '|'.join([d['name'] for d in ser['effects']]),
            ser['system'],
            ser['organ'],
            ser['effect'],
            ser['effect_subtype'],
            ser['observation_time'],
            ser['observation_time_units'],
            ser['observation_time_text'],
            ser['data_location'],
            ser['response_units'],
            ser['data_type'],
            ser['variance_name'],
            ser['confidence_interval'],
            ser['data_reported'],
            ser['data_extracted'],
            ser['values_estimated'],
            ser['expected_adversity_direction_text'],
            ser['monotonicity'],
            ser['statistical_test'],
            ser['trend_value'],
            ser['trend_result'],
            ser['diagnostic'],
            ser['power_notes'],
            cleanHTML(ser['results_notes']),
            cleanHTML(ser['endpoint_notes']),
            json.dumps(ser['additional_fields']),
        )

    @staticmethod
    def get_docx_template_context(assessment, queryset):
        """
        Given a queryset of endpoints, invert the cached results to build
        a top-down data hierarchy from study to endpoint. We use this
        approach since our endpoints are cached, so while it may require
        more computation, its close to free on database access.
        """

        endpoints = [
            SerializerHelper.get_serialized(obj, json=False)
            for obj in queryset
        ]
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
        studies = sorted(
            list(studies.values()),
            key=lambda obj: (obj["short_citation"].lower()))
        for study in studies:
            study["exps"] = sorted(
                list(study["exps"].values()),
                key=lambda obj: (obj["name"].lower()))
            for exp in study["exps"]:
                exp["ags"] = sorted(
                    list(exp["ags"].values()),
                    key=lambda obj: (obj["name"].lower()))
                for ag in exp["ags"]:
                    ag["eps"] = sorted(
                        list(ag["eps"].values()),
                        key=lambda obj: (obj["name"].lower()))

        return {
            "assessment": AssessmentSerializer().to_representation(assessment),
            "studies": studies
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
            g['percentControlMean']
            for g in ep['groups']
            if tryParseInt(g['percentControlMean'], default=False)
        ]
        if len(changes) > 0:
            min_ = min(changes)
            max_ = max(changes)
            val = min_ if abs(min_) > abs(max_) else max_

        ep['percentControlMaxChange'] = val

    def get_latest_bmd_session(self):
        try:
            return self.bmd_sessions.latest()
        except ObjectDoesNotExist:
            return None

    def get_selected_bmd_model(self):
        try:
            return self.bmd_model.model
        except ObjectDoesNotExist:
            return None

    def copy_across_assessments(self, cw):
        children = list(self.groups.all())

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

        # copy tags
        for tag in self.effects.through.objects.filter(baseendpoint_id=old_id):
            tag.id = None
            tag.baseendpoint_id = self.id
            tag.save()

        # copy other children
        for child in children:
            child.copy_across_assessments(cw)


class ConfidenceIntervalsMixin(object):
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
            eg['stdev'] = cls.stdev(variance_type, eg['variance'], eg['n'])

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
                    n_1 = eg['n']
                    mu_1 = eg['response']
                    sd_1 = eg.get('stdev')

                n_2 = eg['n']
                mu_2 = eg['response']
                sd_2 = eg.get('stdev')

                if mu_1 and mu_2 and mu_1 != 0:
                    mean = (mu_2 - mu_1) / mu_1 * 100.
                    if sd_1 and sd_2 and n_1 and n_2:
                        sd = math.sqrt(
                            pow(mu_1, -2) * (
                                (pow(sd_2, 2) / n_2) +
                                (pow(mu_2, 2) * pow(sd_1, 2)) / (n_1 * pow(mu_1,  2))
                            )
                        )
                        ci = (1.96 * sd) * 100
                        rng = sorted([mean - ci, mean + ci])
                        low = rng[0]
                        high = rng[1]

            elif data_type == "P":
                mean = eg['response']
                low = eg['lower_ci']
                high = eg['upper_ci']

            eg.update(percentControlMean=mean, percentControlLow=low, percentControlHigh=high)

    @staticmethod
    def getConfidenceIntervals(data_type, egs):
        """
        Expects a dictionary of endpoint groups and the endpoint data-type.
        Appends results to the dictionary for each endpoint-group.
        """
        for eg in egs:
            lower_ci = eg.get('lower_ci')
            upper_ci = eg.get('upper_ci')
            n = eg.get('n')
            update = False

            if lower_ci is not None or upper_ci is not None or n is None:
                continue

            if (data_type == "C" and eg['response'] is not None and eg['stdev'] is not None):
                """
                Two-tailed t-test, assuming 95% confidence interval.
                """
                se = eg['stdev'] / math.sqrt(n)
                change = stats.t.ppf(0.975, max(n - 1, 1)) * se
                lower_ci = round(eg['response'] - change, 2)
                upper_ci = round(eg['response'] + change, 2)
                update = True
            elif (data_type in ["D", "DC"] and eg['incidence'] is not None):
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
                p = eg['incidence'] / float(n)
                z = stats.norm.ppf(0.975)
                q = 1. - p

                lower_ci = round(
                    ((2 * n * p + 2 * z - 1) - z * math.sqrt(
                        2 * z - (2 + 1 / n) + 4 * p * (n * q + 1))) / (2 * (n + 2 * z)), 2)
                upper_ci = round(
                    ((2 * n * p + 2 * z + 1) + z * math.sqrt(
                        2 * z + (2 + 1 / n) + 4 * p * (n * q - 1))) / (2 * (n + 2 * z)), 2)
                update = True

            if update:
                eg.update(lower_ci=lower_ci, upper_ci=upper_ci)


class EndpointGroup(ConfidenceIntervalsMixin, models.Model):
    objects = managers.EndpointGroupManager()

    endpoint = models.ForeignKey(
        Endpoint,
        related_name='groups')
    dose_group_id = models.IntegerField()
    n = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)])
    incidence = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)])
    response = models.FloatField(
        blank=True,
        null=True)
    variance = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)])
    lower_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Lower CI",
        help_text="Numerical value for lower-confidence interval")
    upper_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Upper CI",
        help_text="Numerical value for upper-confidence interval")
    significant = models.BooleanField(
        default=False,
        verbose_name="Statistically significant from control")
    significance_level = models.FloatField(
        null=True,
        blank=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name="Statistical significance level")

    COPY_NAME = 'groups'

    class Meta:
        ordering = ('endpoint', 'dose_group_id')

    def clean(self):
        self.significant = (self.significance_level is not None and
                            self.significance_level > 0)

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
            return "{}-{}".format(nmin, nmax)

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
            ser['id'],
            ser['dose_group_id'],
            ser['n'],
            ser['incidence'],
            ser['response'],
            ser['variance'],
            ser['lower_ci'],
            ser['upper_ci'],
            ser['significant'],
            ser['significance_level'],
            ser['dose_group_id'] == endpoint['NOEL'],
            ser['dose_group_id'] == endpoint['LOEL'],
            ser['dose_group_id'] == endpoint['FEL'],
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
reversion.register(Endpoint, follow=('groups', ))
reversion.register(EndpointGroup, follow=('endpoint', ))
