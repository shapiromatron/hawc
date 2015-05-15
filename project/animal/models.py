#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import math

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import reversion

from assessment.models import BaseEndpoint, get_cas_url
from assessment.serializers import AssessmentSerializer

from bmd.models import BMD_session
from utils.helper import HAWCDjangoJSONEncoder, SerializerHelper


class Species(models.Model):
    name = models.CharField(
        max_length=30,
        help_text="Enter species in singular (ex: Mouse, not Mice)",
        unique=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "species"
        ordering = ("name", )

    def __unicode__(self):
        return self.name


class Strain(models.Model):
    species = models.ForeignKey(
        Species)
    name = models.CharField(
        max_length=30)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("species", "name"),)
        ordering = ("species", "name")

    def __unicode__(self):
        return self.name


class Experiment(models.Model):

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
        ("N" , "No"),
        ("O" , "Other"))

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
    purity = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Chemical purity (%)",
        help_text="Assumed to be greater-than numeric-value specified (ex: > 95.5%)",
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

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('animal:experiment_detail', args=[str(self.pk)])

    def is_generational(self):
        return self.type in ["Rp", "Dv"]

    def get_assessment(self):
        return self.study.get_assessment()

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
            ser['purity'],
            ser['vehicle'],
            ser['diet'],
            ser['litter_effects'],
            ser['litter_effect_notes'],
            ser['guideline_compliance'],
            ser['description']
        )


class AnimalGroup(models.Model):

    SEX_SYMBOLS = {
        "M": u"♂",
        "F": u"♀",
        "C": u"♂♀",
        "R": u"NR"
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
        ("F4", "Fourth-generation (F4)"))

    experiment = models.ForeignKey(
        Experiment,
        related_name="animal_groups")
    name = models.CharField(
        max_length=80,
        help_text="Short description of the animals (i.e. Male Fischer F344 rats, Female C57BL/6 mice)"
        )
    species = models.ForeignKey(
        Species)
    strain = models.ForeignKey(
        Strain)
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
        blank=True,
        null=True)
    dosing_regime = models.ForeignKey(
        'DosingRegime',
        help_text='Specify an existing dosing regime or create a new dosing regime below',
        blank=True,
        null=True)  # not enforced in db, but enforced in views
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('animal:animal_group_detail', args=[str(self.pk)])

    def get_assessment(self):
        return self.experiment.get_assessment()

    def clean(self):
        #ensure that strain is of the correct species
        try:
            if self.strain.species != self.species:
                raise ValidationError('Error- selected strain is not of the selected species.')
        except:
            raise ValidationError('Error- selected strain is not of the selected species.')

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
            "species-name",
            "strain-name",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            ser['sex'],
            ser['animal_source'],
            ser['lifestage_exposed'],
            ser['lifestage_assessed'],
            ser['duration_observation'],
            ser['siblings'],
            '|'.join([str(p) for p in ser['parents']]),
            ser['generation'],
            ser['species'],
            ser['strain']
        )


class DoseUnits(models.Model):
    units = models.CharField(
        max_length=20,
        unique=True)
    administered = models.BooleanField(
        default=False)
    converted = models.BooleanField(
        default=False)
    hed = models.BooleanField(
        default=False,
        verbose_name="Human Equivalent Dose")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "dose units"

    @property
    def animal_dose_group_count(self):
        return self.dosegroup_set.count()

    @property
    def epi_exposure_count(self):
        return self.exposure_set.count()

    @property
    def invitro_experiment_count(self):
        return self.ivexperiments.count()

    @classmethod
    def json_all(cls):
        return json.dumps(list(cls.objects.all().values()), cls=HAWCDjangoJSONEncoder)

    @classmethod
    def doses_in_assessment(cls, assessment):
        """
        Returns a list of the dose-units which are used in the selected
        assessment for animal bioassay data.
        """
        Study = models.get_model('study', 'Study')
        return DoseUnits.objects.filter(dosegroup__in=
                    DoseGroup.objects.filter(dose_regime__in=
                    DosingRegime.objects.filter(dosed_animals__in=
                    AnimalGroup.objects.filter(experiment__in=
                    Experiment.objects.filter(study__in=
                    Study.objects.filter(assessment=assessment)))))) \
                .values_list('units', flat=True).distinct()

    def __unicode__(self):
        return self.units


class DosingRegime(models.Model):

    ROUTE_EXPOSURE_CHOICES = (
        ("OC", u"Oral capsule"),
        ("OD", u"Oral diet"),
        ("OG", u"Oral gavage"),
        ("OW", u"Oral drinking water"),
        ("I",  u"Inhalation"),
        ("D",  u"Dermal"),
        ("SI", u"Subcutaneous injection"),
        ("IP", u"Intraperitoneal injection"),
        ("IV", u"Intravenous injection"),
        ("IO", u"in ovo"),
        ("P",  u"Parental"),
        ("W",  u"Whole body"),
        ("M",  u"Multiple"),
        ("U",  u"Unknown"),
        ("O",  u"Other"))

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

    def __unicode__(self):
        return u'{0} {1}'.format(self.dosed_animals,
                                 self.get_route_of_exposure_display())

    def get_absolute_url(self):
        return self.dosed_animals.get_absolute_url()

    def get_assessment(self):
        return self.dosed_animals.get_assessment()

    @property
    def dose_groups(self):
        if not hasattr(self, '_dose_groups'):
            self._dose_groups = DoseGroup.objects.select_related('dose_units') \
                                                 .filter(dose_regime=self.pk)
        return self._dose_groups

    def isAnimalsDosed(self, animal_group):
        return self.dosed_animals==animal_group

    @staticmethod
    def flat_complete_header_row():
        return (
            "dosing_regime-id",
            "dosing_regime-dosed_animals",
            "dosing_regime-route_of_exposure",
            "dosing_regime-duration_exposure",
            "dosing_regime-num_dose_groups",
            "dosing_regime-positive_control",
            "dosing_regime-negative_control",
            "dosing_regime-description",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['dosed_animals'],
            ser['route_of_exposure'],
            ser['duration_exposure'],
            ser['num_dose_groups'],
            ser['positive_control'],
            ser['negative_control'],
            ser['description'],
        )

    def get_dose_groups_for_animal_form(self):
        groups = list(self.dose_groups.order_by('dose_group_id', 'dose_units').values('dose_group_id', 'dose_units', 'dose'))
        return json.dumps(groups, cls=HAWCDjangoJSONEncoder)

    def get_dose_groups(self):
        dose_units = []
        dg = self.dose_groups.order_by('dose_group_id', 'dose_units')
        for group in dg.distinct('dose_group_id'):
            dose_units.append(dg.filter(dose_group_id=group.dose_group_id))
        return dose_units

    def get_doses_name_dict(self):
        """
        Return a dictionary where each key are the dose-units and each value is
        a list of doses for this dosing regime of this dose-unit
        """
        doses = {}
        dgs = self.dose_groups.order_by('dose_units', 'dose_group_id')
        for dg in dgs.distinct('dose_units'):
            dose_values = dgs.filter(dose_units=dg.dose_units).values_list('dose', flat=True)
            doses[dg.dose_units.units] = list(dose_values)
        return doses

    def get_doses_json(self, json_encode=True):
        doses = []
        dgs = self.dose_groups.order_by('dose_units', 'dose_group_id')
        for dg in dgs.distinct('dose_units'):
            dose_values = dgs.filter(dose_units=dg.dose_units).values_list('dose', flat=True)
            doses.append({'units': dg.dose_units.units,
                          'units_id': dg.dose_units.pk,
                          'values': list(dose_values)})
        if json_encode:
            return json.dumps(doses, cls=HAWCDjangoJSONEncoder)
        else:
            return doses


class DoseGroup(models.Model):
    dose_regime = models.ForeignKey(
        DosingRegime,
        related_name='doses')
    dose_units = models.ForeignKey(
        DoseUnits)
    dose_group_id = models.PositiveSmallIntegerField()
    dose = models.FloatField(
        validators=[MinValueValidator(0)])
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('dose_units', 'dose_group_id')

    def __unicode__(self):
        return u"{0} {1}".format(self.dose, self.dose_units)

    @classmethod
    def flat_complete_data_row(cls, ser_full, units, idx):
        cols = []
        ser = [ v for v in ser_full if v["dose_group_id"] == idx ]
        for unit in units:
            v = None
            for s in ser:
                if s["dose_units"]["units"] == unit:
                    v = s["dose"]
                    break

            cols.append(v)

        return cols


class Endpoint(BaseEndpoint):

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
        (7, "PND"),
        (8, "GD"))

    TREND_RESULT_CHOICES = (
        (0, "not applicable"),
        (1, "not significant"),
        (2, "significant"),
        (3, "not reported"))

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
    observation_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Numeric value of the time an observation was reported; "
                  "optional, should be recorded if the same effect was measured multiple times.")
    observation_time_units = models.PositiveSmallIntegerField(
        default=0,
        choices=OBSERVATION_TIME_UNITS)
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
                  "(ex: Figure 1, Table 2, etc.)")
    response_units = models.CharField(
        max_length=32,
        verbose_name="Response units",
        help_text=u"Units the response was measured in (i.e., \u03BCg/dL, % control, etc.)")
    data_type = models.CharField(
        max_length=2,
        choices=DATA_TYPE_CHOICES,
        default="D",
        verbose_name="Dataset type")
    variance_type = models.PositiveSmallIntegerField(
        default=0,
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
    individual_animal_data = models.BooleanField(
        default=False,
        help_text="If individual response data are available for each animal.")
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
    qualities = generic.GenericRelation(
        'study.StudyQuality',
        related_query_name='endpoints')

    def get_update_url(self):
        if self.individual_animal_data:
            return reverse('animal:endpoint_individual_animal_update', args=[self.pk])
        else:
            return reverse('animal:endpoint_update', args=[self.pk])

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @classmethod
    def optimized_qs(cls, **filters):
        # Use this method to get proper prefetch and select-related when
        # returning API-style endpoints
        return cls.objects\
            .filter(**filters)\
            .select_related(
                'animal_group',
                'animal_group__dosed_animals',
                'animal_group__experiment',
                'animal_group__experiment__study',
            ).prefetch_related(
                'endpoint_group',
                'effects',
                'animal_group__dosed_animals__doses',
            )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('animal:endpoint_detail', args=[str(self.pk)])

    @property
    def dose_response_available(self):
        return self.data_reported and self.data_extracted

    @property
    def endpoint_groups(self, individual_animal_data=False):
        if not hasattr(self, '_endpoint_groups'):
            related_args = []
            if individual_animal_data:
                related_args = ['endpoint__endpoint_group__individual_data']
            self._endpoint_groups = EndpointGroup.objects.filter(endpoint=self.pk).order_by('dose_group_id').select_related(*related_args)
        return self._endpoint_groups

    def get_endpoint_groups(self):
        return self.endpoint_groups.all()

    def get_m2m_representation(self):
        return u'%s \u279E %s \u279E %s \u279E %s' % (self.animal_group.experiment.study,
                                                      self.animal_group.experiment,
                                                      self.animal_group, self.__unicode__())

    def get_doses_json(self, json_encode=True):
        """
        Return a dictionary containing the doses available for the selected
        endpoint, and also saves a copy to the instance.
        Format is a list: [{'units':'mg/kg/day', 'values':[1,2,3,4]},]
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
    def d_responses(queryset, json_encode=True):
        """
        Return a list of queryset responses with the specified dosing protocol
        """
        endpoints = [e.d_response(json_encode=False) for e in queryset]
        if json_encode:
            return json.dumps(endpoints, cls=HAWCDjangoJSONEncoder)
        else:
            return endpoints

    def d_response(self, json_encode=True):
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
        egs = self.endpoint_groups.all()
        if self.data_type != 'C':
            return True  # dichotomous datasets increase by default
        change = 0
        for i in xrange(1, len(egs)):
            change += egs[i].response - egs[0].response
        return change >= 0

    def bmds_session_exists(self):
        """
        Check if at least one BMDS session exists for the specified Endpoint ID.
        """
        return BMD_session.objects.filter(endpoint=self.pk).count() > 0

    def get_bmds_session(self):
        """
        Return BMDS session
        """
        try:
            return BMD_session.objects.filter(endpoint=self.pk).latest('last_updated')
        except:
            return None

    @classmethod
    def flat_complete_header_row(cls):
        return (
            "endpoint-id",
            "endpoint-url",
            "endpoint-name",
            "endpoint-effects",
            "endpoint-system",
            "endpoint-organ",
            "endpoint-effect",
            "endpoint-observation_time",
            "endpoint-observation_time_units",
            "endpoint-data_location",
            "endpoint-response_units",
            "endpoint-data_type",
            "endpoint-variance_type",
            "endpoint-confidence_interval",
            "endpoint-data_reported",
            "endpoint-data_extracted",
            "endpoint-values_estimated",
            "endpoint-individual_animal_data",
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

    @classmethod
    def flat_complete_data_row(cls, ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            '|'.join([ d['name'] for d in ser['effects'] ]),
            ser['system'],
            ser['organ'],
            ser['effect'],
            ser['observation_time'],
            ser['observation_time_units'],
            ser['data_location'],
            ser['response_units'],
            ser['data_type'],
            ser['variance_name'],
            ser['confidence_interval'],
            ser['data_reported'],
            ser['data_extracted'],
            ser['values_estimated'],
            ser['individual_animal_data'],
            ser['monotonicity'],
            ser['statistical_test'],
            ser['trend_value'],
            ser['trend_result'],
            ser['diagnostic'],
            ser['power_notes'],
            ser['results_notes'],
            ser['endpoint_notes'],
            json.dumps(ser['additional_fields']),
        )

    @classmethod
    def get_docx_template_context(cls, assessment, queryset):
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
                study["exps"][exp["id"]]  = exp

            ag = exp["ags"].get(thisAG["id"])
            if ag is None:
                ag = thisAG
                ag["eps"] = {}
                exp["ags"][ag["id"]]  = ag

            ep = ag["eps"].get(thisEp["id"])
            if ep is None:
                ep = thisEp
                ag["eps"][ep["id"]]  = ep

        # convert value dictionaries to lists
        studies = sorted(
            studies.values(),
            key=lambda obj: (obj["short_citation"].lower()))
        for study in studies:
            study["exps"] = sorted(
                study["exps"].values(),
                key=lambda obj: (obj["name"].lower()))
            for exp in study["exps"]:
                exp["ags"] = sorted(
                    exp["ags"].values(),
                    key=lambda obj: (obj["name"].lower()))
                for ag in exp["ags"]:
                    ag["eps"] = sorted(
                        ag["eps"].values(),
                        key=lambda obj: (obj["name"].lower()))

        return {
            "assessment": AssessmentSerializer().to_representation(assessment),
            "studies": studies
        }

    @classmethod
    def get_system_choices(cls, assessment_id):
        objs = cls.objects\
                  .filter(assessment_id=assessment_id)\
                  .distinct('system')\
                  .values_list('system', flat=True)
        return [ (obj, obj) for obj in sorted(objs) ]

    @classmethod
    def get_effect_choices(cls, assessment_id):
        objs = cls.objects\
                  .filter(assessment_id=assessment_id)\
                  .distinct('effect')\
                  .values_list('effect', flat=True)
        return [ (obj, obj) for obj in sorted(objs) ]


class EndpointGroup(models.Model):
    endpoint = models.ForeignKey(
        Endpoint,
        related_name='endpoint_group')
    dose_group_id = models.IntegerField()
    n = models.PositiveSmallIntegerField(
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
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name="Statistical significance level")

    class Meta:
        ordering = ('endpoint', 'dose_group_id')

    def clean(self):
        self.significant = (self.significance_level > 0)

    @property
    def hasVariance(self):
        return self.variance is not None

    @classmethod
    def getIndividuals(cls, endpoint, egs):
        individuals = cls.objects.filter(endpoint=endpoint.id)\
                         .select_related('endpoint_group__individual_data')\
                         .values('dose_group_id', 'individual_data__response')

        for i, eg in enumerate(egs):
            eg['individual_responses'] = [
                    v['individual_data__response']
                    for v in individuals
                    if v['dose_group_id'] == eg['dose_group_id']
                ]

    @staticmethod
    def stdev(variance_type, variance, n):
        # calculate stdev given re
        if variance_type == 1:
            return variance
        elif variance and variance_type == 2:
            return variance * math.sqrt(n)
        else:
            return None

    def getStdev(self, variance_type=None):
        """ Return the stdev of an endpoint-group, given the variance type. """
        if not hasattr(self, "_stdev"):

            # don't hit DB unless we need to
            if variance_type is None:
                variance_type = self.endpoint.variance_type

            self._stdev = EndpointGroup.stdev(variance_type, self.variance, self.n)

        return self._stdev

    @staticmethod
    def getStdevs(variance_type, egs):
        for eg in egs:
            eg['stdev'] = EndpointGroup.stdev(variance_type, eg['variance'], eg['n'])

    @staticmethod
    def percentControl(data_type, egs):
        #
        # Expects a dictionary of endpoint groups and the endpoint data-type.
        # Appends results to the dictionary for each endpoint-group.
        #
        # Calculates a 95% confidence interval for the percent-difference from
        # control, taking into account variance from both groups using a
        # Fisher Information Matrix, assuming independent normal distributions.
        #
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

                if mu_1 != 0 and sd_1 and sd_2:
                    mean = (mu_2-mu_1) / mu_1 * 100.
                    sd = math.sqrt(
                        math.pow(mu_1, -2) * (
                            (math.pow(sd_2, 2)/n_2) +
                            (math.pow(mu_2, 2)*math.pow(sd_1, 2)) / (n_1*math.pow(mu_1, 2))
                        )
                    )
                    ci   = (1.96 * sd) * 100
                    rng  = sorted([ mean - ci, mean + ci ])
                    low  = rng[0]
                    high = rng[1]

            elif data_type == "P":
                mean = eg['response']
                low  = eg['lower_ci']
                high = eg['upper_ci']

            eg.update(percentControlMean=mean, percentControlLow=low, percentControlHigh=high)

    @staticmethod
    def getNRangeText(ns):
        """
        Given a list of N values, return textual range of N values in the list.
        For example, may return "10-12", "7", or "Not available".
        """
        if len(ns)==0:
            return "Not available"
        nmin = min(ns)
        nmax = max(ns)
        if nmin==nmax:
            return unicode(nmin)
        else:
            return u"{}-{}".format(nmin, nmax)

    @classmethod
    def flat_complete_header_row(cls):
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

    @classmethod
    def flat_complete_data_row(cls, ser, endpoint):
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
            ser['dose_group_id']==endpoint['NOEL'],
            ser['dose_group_id']==endpoint['LOEL'],
            ser['dose_group_id']==endpoint['FEL'],
        )


class IndividualAnimal(models.Model):
    endpoint_group = models.ForeignKey(
        EndpointGroup,
        related_name='individual_data')
    response = models.FloatField()

    def __unicode__(self):
        return str(self.response)


class UncertaintyFactorAbstract(models.Model):

    UF_TYPE_CHOICES = (
        ('UFA', 'Interspecies uncertainty'),
        ('UFH', 'Intraspecies variability'),
        ('UFS', 'Subchronic to chronic extrapolation'),
        ('UFL', 'Use of a LOAEL in absence of a NOAEL'),
        ('UFD', 'Database incomplete'),
        ('UFO', 'Other'))

    uf_type = models.CharField(
        max_length=3,
        choices=UF_TYPE_CHOICES,
        verbose_name="Uncertainty Value Type")
    value = models.FloatField(
        default=10.,
        help_text="Note that 3*3=10 for all uncertainty value calculations; "
                  "therefore specifying 3.33 is not required.",
        validators=[MinValueValidator(1)])
    description = models.TextField(
        blank=True,
        verbose_name='Justification')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)  # standardize changed to updated

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.get_uf_type_display()

    def get_absolute_url(self):
        return reverse('animal:uf_detail', args=[self.pk])

    def get_dictionary(self):
        d = {}
        fields = ['pk', 'uf_type', 'value', 'description']
        for field in fields:
            d[field] = getattr(self, field)
        d['url'] = self.get_absolute_url()
        return d


class UncertaintyFactorEndpoint(UncertaintyFactorAbstract):
    endpoint = models.ForeignKey(
        Endpoint,
        related_name='ufs')

    class Meta(UncertaintyFactorAbstract.Meta):
        unique_together = (("endpoint", "uf_type"),)

    def clean(self):
        #ensure that only only UF type of the same type exists for an endpoint
        #unique_together constraint checked above; not done in form because endpoint is excluded
        pk_exclusion = {}
        if self.pk:
            pk_exclusion['pk'] = self.pk
        if UncertaintyFactorEndpoint.objects.filter(endpoint=self.endpoint, uf_type=self.uf_type).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- uncertainty factor type already exists for this endpoint.')

    def get_assessment(self):
        return self.endpoint.get_assessment()

    def get_dictionary(self):
        d = super(UncertaintyFactorEndpoint, self).get_dictionary()
        d['endpoint'] = self.endpoint.pk
        return d


class UncertaintyFactorRefVal(UncertaintyFactorAbstract):
    reference_value = models.ForeignKey(
        'ReferenceValue',
        related_name='ufs')

    class Meta(UncertaintyFactorAbstract.Meta):
        unique_together = (("reference_value", "uf_type"),)

    def clean(self):
        #ensure that only only UF type of the same type exists for a reference value
        #unique_together constraint checked above; not done in form because reference value is excluded
        if hasattr(self, 'reference_value'):
            pk_exclusion = {}
            if self.pk:
                pk_exclusion['pk'] = self.pk
            if UncertaintyFactorRefVal.objects.filter(reference_value=self.reference_value, uf_type=self.uf_type).exclude(**pk_exclusion).count() > 0:
                raise ValidationError('Error- uncertainty factor type already exists for this reference value.')

    def get_assessment(self):
        return self.reference_value.get_assessment()

    def get_dictionary(self):
        d = super(UncertaintyFactorRefVal, self).get_dictionary()
        d['reference_value'] = self.reference_value.pk
        return d


class Aggregation(models.Model):

    AGGREGATION_TYPE_CHOICES = (
        ('E', 'Evidence'),
        ('M', 'Mode-of-action'),
        ('CD', 'Candidate Reference Values'))

    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='aggregation')
    dose_units = models.ForeignKey(
        DoseUnits)
    name = models.CharField(
        max_length=100)
    aggregation_type = models.CharField(
        max_length=2,
        choices=AGGREGATION_TYPE_CHOICES,
        default="E",
        help_text="The purpose for creating this aggregation.")
    endpoints = models.ManyToManyField(
        Endpoint,
        related_name='aggregation',
        help_text="All endpoints entered for assessment.")
    summary_text = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('animal:aggregation_detail', args=[str(self.pk)])

    def get_assessment(self):
        return self.assessment

    def get_endpoints_json(self, json_encode=True):
        return Endpoint.d_responses(
                self.endpoints.all(),
                json_encode=json_encode)

    def get_prior_versions_json(self):
        """
        Return a JSON list of other prior versions of selected model
        """
        def get_endpoints(pk_list):
            endpoints = []
            for pk in pk_list:
                try:
                    u = Endpoint.objects.get(pk=pk)
                except:
                    deleted_endpoints = reversion.get_deleted(Endpoint)
                    u = deleted_endpoints.get(pk=pk)
                endpoints.append(unicode(u))
            return '<br>'.join(sorted(endpoints))

        def get_foo_display(selected, choices, default=None):
            # try to find a match, if none is found return existing value
            for choice in choices:
                if choice[0] == selected:
                    return choice[1]
            return default or selected

        versions = reversion.get_for_object(self)
        versions_json = []
        for version in versions:
            fields = version.field_dict
            fields['aggregation_type'] = get_foo_display(
                    fields['aggregation_type'], Aggregation.AGGREGATION_TYPE_CHOICES)
            fields['changed_by'] = version.revision.user.get_full_name()
            fields['updated'] = version.revision.date_created
            fields['endpoints'] = get_endpoints(fields['endpoints'])
            fields.pop('assessment')
            versions_json.append(fields)
        return json.dumps(versions_json, cls=HAWCDjangoJSONEncoder)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode, from_cache=False)


class ReferenceValue(models.Model):

    REFERENCE_VALUE_CHOICES = (
        (1, 'Oral RfD'),
        (2, 'Inhalation RfD'),
        (3, 'Oral CSF'),
        (4, 'Inhalation CSF'))

    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='reference_values')
    point_of_departure = models.FloatField(
        validators=[MinValueValidator(0)])
    type = models.PositiveSmallIntegerField(
        choices=REFERENCE_VALUE_CHOICES,
        default=1)
    units = models.ForeignKey(
        DoseUnits,
        related_name='units+')
    justification = models.TextField()
    aggregation = models.ForeignKey(
        Aggregation,
        help_text="Specify a collection of endpoints which justify this reference-value")
    aggregate_uf = models.FloatField(
        blank=True)
    reference_value = models.FloatField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("assessment", "type", "units"),)

    def __unicode__(self):
        return u'{type_display} ({units})'.format(type_display=self.get_type_display(),
                                                  units=self.units)

    def get_absolute_url(self):
        return reverse('animal:ref_val', args=[self.pk])

    def get_assessment(self):
        return self.assessment

    def calculate_reference_value(self, ufs_list=None):
        return (self.point_of_departure / self.calculate_total_uncertainty_value(ufs_list))

    def calculate_total_uncertainty_value(self, ufs_list=None):
        # in RfD math, 3*3=10.

        def approx_equal(x, y, tolerance=0.001):
            return abs(x-y) <= 0.5 * tolerance * (x + y)

        aggregate_uf = 1.
        threes = 0

        if ufs_list is None:
            ufs_list = list(self.ufs.values_list('value', flat=True))

        for uf in ufs_list:
            if approx_equal(uf, 3.):
                threes += 1
            else:
                aggregate_uf *= uf
        aggregate_uf *= 10**(threes / 2)
        aggregate_uf *= 3 if threes % 2 != 0 else 1
        return aggregate_uf

    def clean(self):
        #Ensure the unique_together constraint is checked above. Added explicitly
        # here because assessment is excluded in form display of this
        if hasattr(self, "units") is False:
            raise ValidationError("Error- units are required.")

        pk_exclusion = {}
        if self.pk:
            pk_exclusion['pk'] = self.pk
        if ReferenceValue.objects.filter(assessment=self.assessment,
                                         type=self.type,
                                         units=self.units)\
                                 .exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- reference value factor type already exists for this combination of assessment, reference-type, and units.')

    def get_json(self, json_encode=True):
        fields = ['pk', 'point_of_departure', 'justification', 'created', 'last_updated']
        d = {'type': self.get_type_display(),
             'assessment_url': self.assessment.get_absolute_url(),
             'aggregation_url': self.aggregation.get_absolute_url(),
             'units': self.units.__unicode__(),
             'name': self.__unicode__(),
             'uf_total': self.calculate_total_uncertainty_value(),
             'rfd': self.calculate_reference_value()}
        for field in fields:
            d[field] = getattr(self, field)
        d['ufs'] = []
        for uf in self.ufs.all():
            d['ufs'].append(uf.get_dictionary())
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    def save_meta_information(self, formset):
        # additional information must be saved to the django model, but
        # this data requires the cleaned formset to save.
        ufs = []
        for form in formset:
            ufs.append(form.cleaned_data['value'])
        self.aggregate_uf = self.calculate_total_uncertainty_value(ufs)
        self.reference_value = self.calculate_reference_value(ufs)
        self.save()


@receiver(post_save, sender=Experiment)
@receiver(pre_delete, sender=Experiment)
@receiver(post_save, sender=AnimalGroup)
@receiver(pre_delete, sender=AnimalGroup)
@receiver(post_save, sender=DosingRegime)
@receiver(pre_delete, sender=DosingRegime)
@receiver(post_save, sender=Endpoint)
@receiver(pre_delete, sender=Endpoint)
@receiver(post_save, sender=EndpointGroup)
@receiver(pre_delete, sender=EndpointGroup)
@receiver(post_save, sender=UncertaintyFactorEndpoint)
@receiver(pre_delete, sender=UncertaintyFactorEndpoint)
def invalidate_endpoint_cache(sender, instance, **kwargs):
    instance_type = type(instance)
    filters = {}
    if instance_type is Experiment:
        filters["animal_group__experiment"] = instance.id
    elif instance_type is AnimalGroup:
        filters["animal_group"] = instance.id
    elif instance_type is DosingRegime:
        filters["animal_group__dosing_regime"] = instance.id
    elif instance_type is Endpoint:
        ids = [instance.id]
    elif instance_type is EndpointGroup:
        ids = [instance.endpoint_id]
    elif instance_type is UncertaintyFactorEndpoint:
        ids = [instance.endpoint_id]

    if len(filters)>0:
        ids = Endpoint.objects.filter(**filters).values_list('id', flat=True)

    Endpoint.delete_caches(ids)


reversion.register(Species)
reversion.register(Strain)
reversion.register(Experiment)
reversion.register(AnimalGroup)
reversion.register(DoseUnits)
reversion.register(DosingRegime)
# need to modify Update view to make this viable
#reversion.register(IndividualAnimal)
reversion.register(DoseGroup)
reversion.register(Endpoint)
reversion.register(UncertaintyFactorEndpoint)
reversion.register(UncertaintyFactorRefVal)
reversion.register(Aggregation)
reversion.register(ReferenceValue)
