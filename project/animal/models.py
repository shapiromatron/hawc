from collections import Counter, OrderedDict
import copy
import json
import logging
import math

from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

import reversion

from assessment.models import BaseEndpoint
from assessment.tasks import get_chemspider_details
from bmd.models import BMD_session
from utils.helper import (HAWCDjangoJSONEncoder, build_excel_file, build_tsv_file,
                          HAWCdocx, excel_export_detail)


class Species(models.Model):
    name = models.CharField(
        max_length=30,
        help_text="Enter species in singular (ex: Mouse, not Mice)",
        unique=True)
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "species"

    def __unicode__(self):
        return self.name

    def getDict(self):
        """
        Return flat-dictionary of species.
        """
        return OrderedDict((("species-pk", self.pk),
                            ("species-name", self.name)))

    @staticmethod
    def excel_export_detail(dic, isHeader):
        return excel_export_detail(dic, isHeader)


class Strain(models.Model):
    species = models.ForeignKey(
        Species)
    name = models.CharField(
        max_length=30)
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = (("species", "name"),)

    def __unicode__(self):
        return self.name

    def getDict(self):
        """
        Return flat-dictionary of strain.
        """
        return OrderedDict((("strain-pk", self.pk),
                            ("strain-name", self.name)))

    @staticmethod
    def excel_export_detail(dic, isHeader):
        return excel_export_detail(dic, isHeader)


SEX_CHOICES = (("M", "Male"),
               ("F", "Female"),
               ("B", "Both"))

GENERATION_CHOICES = (("F0", "Parent-Generation (F0)"),
                      ("F1", "First-Generation (F1)"),
                      ("F2", "Second-Generation (F2)"))

EXPERIMENT_TYPE_CHOICES = (("Ac", "Acute"),
                           ("Sb", "Subchronic"),
                           ("Ch", "Chronic"),
                           ("Ca", "Cancer"),
                           ("Me", "Mechanistic"),
                           ("Rp", "Reproductive"),
                           ("Dv", "Developmental"),
                           ("Ot", "Other"))


class Experiment(models.Model):
    study = models.ForeignKey(
        'study.Study',
        related_name='experiments')
    name = models.CharField(
        max_length=80)
    type = models.CharField(
        max_length=2,
        choices=EXPERIMENT_TYPE_CHOICES)
    cas = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Chemical identifier (CAS)")
    purity_available = models.BooleanField(
        default=True,
        verbose_name="Chemical purity available?")
    purity = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Chemical purity (%)",
        help_text="Assumed to be greater-than numeric-value specified (ex: > 95.5%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    description = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Experiment, self).save(*args, **kwargs)
        endpoint_pks = list(Endpoint.objects.all()
                            .filter(animal_group__experiment=self.pk)
                            .values_list('pk', flat=True))
        Endpoint.d_response_delete_cache(endpoint_pks)

    def get_absolute_url(self):
        return reverse('animal:experiment_detail', args=[str(self.pk)])

    def is_generational(self):
        return self.type in ["Rp", "Dv"]

    def get_assessment(self):
        return self.study.get_assessment()

    def get_CAS_details(self):
        task = get_chemspider_details.delay(self.cas)
        v = task.get(timeout=60)
        if v:
            return v

    def getDict(self):
        """
        Return flat-dictionary of experiment.
        """
        return OrderedDict((
            ("experiment-pk", self.pk),
            ("experiment-url", self.get_absolute_url()),
            ("experiment-name", self.name),
            ("experiment-type", self.name),
            ("experiment-cas", self.cas),
            ("experiment-purity_available", self.purity_available),
            ("experiment-purity", self.purity),
            ("experiment-description", self.description)
        ))

    @staticmethod
    def excel_export_detail(dic, isHeader):
        return excel_export_detail(dic, isHeader)


class AnimalGroup(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        related_name="animal_groups")
    name = models.CharField(
        max_length=80)
    species = models.ForeignKey(
        Species)
    strain = models.ForeignKey(
        Strain)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES)
    dose_groups = models.PositiveSmallIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        verbose_name="Number of Dose Groups")
    duration_observation = models.FloatField(
        verbose_name="Observation duration (days)",
        help_text="Length of observation period, in days (fractions allowed)",
        blank=True,
        null=True)
    siblings = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    dosing_regime = models.ForeignKey(
        'DosingRegime',
        help_text='Specify an existing dosing regime or create a new dosing regime below',
        blank=True,
        null=True)  # not enforced in db, but enforced in views
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('animal:animal_group_detail', args=[str(self.pk)])

    def save(self, *args, **kwargs):
        super(AnimalGroup, self).save(*args, **kwargs)
        endpoint_pks = list(Endpoint.objects.all()
                            .filter(animal_group=self.pk)
                            .values_list('pk', flat=True))
        Endpoint.d_response_delete_cache(endpoint_pks)

    def get_assessment(self):
        return self.experiment.get_assessment()

    def clean(self):
        #ensure that strain is of the correct species
        try:
            if self.strain.species != self.species:
                raise ValidationError('Error- selected strain is not of the selected species.')
        except:
            raise ValidationError('Error- selected strain is not of the selected species.')

    def get_doses_json(self, json_encode=True):
        if not hasattr(self, 'doses'):
            self.doses = [{"error": "no dosing regime"}]
            self.doses = self.dosing_regime.get_doses_json(False)
        if json_encode:
            return json.dumps(self.doses, cls=HAWCDjangoJSONEncoder)
        return self.doses

    def get_endpoints(self):
        return Endpoint.objects.filter(animal_group=self.pk)

    def get_siblings_pk(self):
        try:
            return self.siblings.pk
        except:
            return None

    def getDict(self):
        """
        Return flat-dictionary of AnimalGroup.
        """
        d = OrderedDict((
            ("animal_group-pk", self.pk),
            ("animal_group-url", self.get_absolute_url()),
            ("animal_group-name", self.name),
            ("animal_group-sex", self.get_sex_display()),
            ("animal_group-dose_groups", self.dose_groups),
            ("animal_group-duration_observation", self.duration_observation),
            ("animal_group-siblings", self.get_siblings_pk()),
            ("animal_group-parents", "N/A")
        ))
        d['_species'] = self.species.getDict()
        d['_strain'] = self.strain.getDict()
        d['_dosing_regime'] = self.dosing_regime.getDict(self)
        if hasattr(self, "generationalanimalgroup"):
            d.update(self.generationalanimalgroup.getDict())
        return d

    @staticmethod
    def excel_export_detail(dic, isHeader):
        return excel_export_detail(dic, isHeader)


class GenerationalAnimalGroup(AnimalGroup):
    generation = models.CharField(
        max_length=2,
        choices=GENERATION_CHOICES)
    parents = models.ManyToManyField(
        "self",
        related_name="parents+",
        symmetrical=False,
        blank=True,
        null=True)

    def __unicode__(self):
        return self.name

    def get_children(self):
        return GenerationalAnimalGroup.objects.filter(parents=self)

    def get_parent_pks(self):
        return self.parents.all().values_list('pk', flat=True)

    def getDict(self):
        """
        Return flat-dictionary of GenerationalAnimalGroup.
        """
        parent_pks = '|'.join([str(par) for par in self.get_parent_pks()])
        return OrderedDict(( ('animal_group-parents', parent_pks), ))


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
    updated = models.DateTimeField(
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
        return self.experiment_set.count()

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
        return DoseGroup.objects.filter(dose_regime__in=
                    DosingRegime.objects.filter(dosed_animals__in=
                    AnimalGroup.objects.filter(experiment__in=
                    Experiment.objects.filter(study__in=
                    Study.objects.filter(assessment=assessment))))) \
                .values_list('dose_units__units', flat=True).distinct()

    def __unicode__(self):
        return self.units

    def getDict(self):
        """
        Return flat-dictionary of DoseUnits.
        """
        return {"dose_units-pk": self.pk,
                "dose_units-units": self.units}


ROUTE_EXPOSURE = (("OD", u"Oral diet"),
                  ("OG", u"Oral gavage"),
                  ("OW", u"Oral drinking water"),
                  ("I",  u"Inhalation"),
                  ("D",  u"Dermal"),
                  ("SI", u"Subcutaneous injection"),
                  ("IP", u"Intraperitoneal injection"),
                  ("IO", u"in ovo"),
                  ("O",  u"Other"))


class DosingRegime(models.Model):
    dosed_animals = models.OneToOneField(
        AnimalGroup,
        related_name='dosed_animals',
        blank=True,
        null=True)
    route_of_exposure = models.CharField(
        max_length=2,
        choices=ROUTE_EXPOSURE)
    duration_exposure = models.FloatField(
        verbose_name="Exposure duration (days)",
        help_text="Length of exposure period, in days (fractions allowed)",
        blank=True,
        null=True)
    description = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)

    def __unicode__(self):
        return u'{0} {1}'.format(self.dosed_animals,
                                 self.get_route_of_exposure_display())

    def get_absolute_url(self):
        return reverse('animal:dosing_regime_detail', args=[str(self.pk)])

    def get_assessment(self):
        return self.dosed_animals.get_assessment()

    def save(self, *args, **kwargs):
        super(DosingRegime, self).save(*args, **kwargs)
        endpoint_pks = list(Endpoint.objects.all()
                            .filter(animal_group__dosing_regime=self.pk)
                            .values_list('pk', flat=True))
        Endpoint.d_response_delete_cache(endpoint_pks)

    @property
    def dose_groups(self):
        if not hasattr(self, '_dose_groups'):
            self._dose_groups = DoseGroup.objects.select_related('dose_units') \
                                                 .filter(dose_regime=self.pk)
        return self._dose_groups

    def isAnimalsDosed(self, animal_group):
        return self.dosed_animals==animal_group

    def getDict(self, animal_group):
        """
        Return ordered dictionary of DosingRegime.
        """
        d = OrderedDict((
                ("dosing_regime-pk", self.pk),
                ("dosing_regime-dosed_animals", self.isAnimalsDosed(animal_group)),
                ("dosing_regime-route_of_exposure", self.get_route_of_exposure_display()),
                ("dosing_regime-duration_exposure", self.duration_exposure),
                ("dosing_regime-description", self.description)))
        d['_doses'] = self.get_doses_name_dict()
        return d

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

    @staticmethod
    def excel_export_detail(dic, isHeader):
        return excel_export_detail(dic, isHeader)


class DoseGroup(models.Model):
    dose_regime = models.ForeignKey(
        DosingRegime,
        related_name='doses')
    dose_units = models.ForeignKey(
        DoseUnits)
    dose_group_id = models.PositiveSmallIntegerField()
    dose = models.DecimalField(
        max_digits=50,
        decimal_places=25,
        blank=False,
        validators=[MinValueValidator(0)])
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)

    def save(self, *args, **kwargs):
        super(DoseGroup, self).save(*args, **kwargs)
        endpoint_pks = list(Endpoint.objects.all()
                            .filter(animal_group__dosing_regime__doses=self.pk)
                            .values_list('pk', flat=True))
        Endpoint.d_response_delete_cache(endpoint_pks)

    def __unicode__(self):
        return str(float(self.dose)) + ' (' + self.dose_units.__unicode__() + ')'

    def get_float_dose(self):
        return float(self.dose)

    @classmethod
    def clean_formset(cls, dose_groups, number_dose_groups):
        """
        Ensure that the selected dose_groups fields have an number of dose_groups
        equal to those expected from the animal dose group, and that all dose
        ids have all dose groups.
        """
        if len(dose_groups) < 1:
            raise ValidationError("<ul><li>At least one set of dose-units must be presented!</li></ul>")
        dose_units = Counter()
        dose_group = Counter()
        for dose in dose_groups:
            dose_units[dose['dose_units']] += 1
            dose_group[dose['dose_group_id']] += 1
        for dose_unit in dose_units.itervalues():
            if dose_unit != number_dose_groups:
                raise ValidationError('<ul><li>Each dose-type must have ' + str(number_dose_groups) + ' dose groups</li></ul>')
        if not all(dose_group.values()[0] == group for group in dose_group.values()):
            raise ValidationError('<ul><li>All dose ids must be equal to the same number of values</li></ul>')


DATA_TYPE_CHOICES = (('C', 'Continuous'),
                     ('D', 'Dichotomous'),
                     ('DC', 'Dichotomous Cancer'),
                     ('NR', 'Not reported'))

MONOTONICITY_CHOICES = ((0, "N/A, single dose level study"),
                        (1, "N/A, no effects detected"),
                        (2, "yes, visual appearance of monotonicity but no trend"),
                        (3, "yes, monotonic and significant trend"),
                        (4, "yes, visual appearance of non-monotonic but no trend"),
                        (5, "yes, non-monotonic and significant trend"),
                        (6, "no pattern"),
                        (7, "unclear"),
                        (8, "not-reported"))

VARIANCE_TYPE_CHOICES = ((0, "NA"),
                         (1, "SD"),
                         (2, "SE"))

VARIANCE_NAME = {
    0: "N/A",
    1: "Standard Deviation",
    2: "Standard Error"}


class Endpoint(BaseEndpoint):
    animal_group = models.ForeignKey(
        AnimalGroup)
    system = models.CharField(
        max_length=128,
        blank=True)
    organ = models.CharField(
        max_length=128,
        blank=True)
    effect = models.CharField(
        max_length=128,
        blank=True)
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)")
    response_units = models.CharField(
        max_length=15,
        verbose_name="Response units")
    data_type = models.CharField(
        max_length=2,
        choices=DATA_TYPE_CHOICES,
        default="D",
        verbose_name="Dataset type")
    variance_type = models.PositiveSmallIntegerField(
        default=0,
        choices=VARIANCE_TYPE_CHOICES)
    NOAEL = models.SmallIntegerField(
        verbose_name="NOAEL",
        default=-999)
    LOAEL = models.SmallIntegerField(
        verbose_name="LOAEL",
        default=-999)
    FEL = models.SmallIntegerField(
        verbose_name="FEL",
        default=-999)
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
        choices=MONOTONICITY_CHOICES)
    statistical_test = models.CharField(
        max_length=256,
        blank=True)
    trend_value = models.FloatField(
        null=True,
        blank=True)
    results_notes = models.TextField(
        blank=True,
        help_text="Qualitative description of the results")
    endpoint_notes = models.TextField(
        blank=True,
        help_text="Any additional notes related to this endpoint itself, not related to results")
    additional_fields = models.TextField(
        default="{}")

    def getDict(self, target=False):
        """
        Return flat-dictionary of Endpoint.

        Target indicates if all parent/child relationships should be fetched
        for this Endpoint.
        """
        d = super(Endpoint, self).getDict()
        d.update(OrderedDict((
            ("endpoint-pk", self.pk),
            ("endpoint-url", self.get_absolute_url()),
            ("endpoint-system", self.system),
            ("endpoint-organ", self.organ),
            ("endpoint-effect", self.effect),
            ("endpoint-data_location", self.data_location),
            ("endpoint-response_units", self.response_units),
            ("endpoint-data_type", self.get_data_type_display()),
            ("endpoint-variance_type", self.variance_name),
            ("endpoint-NOAEL", self.NOAEL),
            ("endpoint-LOAEL", self.LOAEL),
            ("endpoint-FEL", self.FEL),
            ("endpoint-data_reported", self.data_reported),
            ("endpoint-data_extracted", self.data_extracted),
            ("endpoint-values_estimated", self.values_estimated),
            ("endpoint-individual_animal_data", self.individual_animal_data),
            ("endpoint-monotonicity", self.get_monotonicity_display()),
            ("endpoint-statistical_test", self.statistical_test),
            ("endpoint-trend_value", self.trend_value),
            ("endpoint-results_notes", self.results_notes),
            ("endpoint-endpoint_notes", self.endpoint_notes),
            ("endpoint-additional_fields", self.additional_fields),
        )))

        egs = []
        if target:
            d['_study'] = self.animal_group.experiment.study.getDict()
            d['_experiment'] = self.animal_group.experiment.getDict()
            d['_animal_group'] = self.animal_group.getDict()
            for eg in self.endpoint_group.all():
                egs.append(eg.getDict())
            d['_endpoint_groups'] = egs

        return d

    def get_update_url(self):
        if self.individual_animal_data:
            return reverse('animal:endpoint_individual_animal_update', args=[self.pk])
        else:
            return reverse('animal:endpoint_update', args=[self.pk])

    def save(self, *args, **kwargs):
        super(Endpoint, self).save(*args, **kwargs)
        Endpoint.d_response_delete_cache([self.pk])

    def flat_file_row(self, dose=None):
        dose_pk = dose.pk if dose else None
        d = self.d_response(json_encode=False, dose_pk=dose_pk)
        rows = []

        def get_dose_list(d):
            doses = u', '.join([str(float(v['dose'])) for v in d['dr']])
            return u"{0} {1}".format(doses, d["dose_units"])

        # build-base row which is endpoint-group independent
        base = [d['study']['short_citation'],
                d['study']['study_url'],
                d['study']['pk'],
                d['experiment'],
                d['experiment_url'],
                d['animal_group'],
                d['animal_group_url'],
                d['name'],
                d['url'],
                self.get_data_type_display(),
                get_dose_list(d),
                d['dose_units'],
                d['response_units'],
                d['pk']]

        # dose-group specific information
        if len(d['dr'])>0:
            base.extend([
                d['dr'][1]['dose'],
                d['dr'][d['NOAEL']]['dose'] if d['NOAEL'] != -999 else None,
                d['dr'][d['LOAEL']]['dose'] if d['LOAEL'] != -999 else None,
                d['dr'][d['FEL']]['dose'] if d['FEL'] != -999 else None,
                d['dr'][len(d['dr'])-1]['dose']
            ])
        else:
            base.extend([None]*5)

        # BMD-specific information
        if d['BMD'] and d['BMD'].has_key('outputs') and d['BMD']['dose_units_id'] == dose_pk:
            base.extend([
                d['BMD']['outputs']['model_name'],
                d['BMD']['outputs']['BMDL'],
                d['BMD']['outputs']['BMD'],
                d['BMD']['outputs']['BMDU'],
                d['BMD']['outputs']['CSF']
            ])
        else:
            base.extend([None]*5)

        # endpoint-group information
        for i, v in enumerate(d['dr']):
            row = copy.copy(base)
            row.extend([
                i,
                v['dose'],
                v['n'],
                v['incidence'],
                v['response'],
                v['stdev'],
                v['percentControlMean'],
                v['percentControlLow'],
                v['percentControlHigh']
            ])
            rows.append(row)

        return rows

    @classmethod
    def d_response_delete_cache(cls, endpoint_pks):
        super(Endpoint, cls).d_response_delete_cache(endpoint_pks)
        if len(endpoint_pks)>0:
            assessment = BaseEndpoint.objects.get(pk=endpoint_pks[0]).assessment
            xls_cache = Endpoint.xls_export_cache_name(assessment)
            logging.info('removing cache: {cache}'.format(cache=xls_cache))
            cache.delete(xls_cache)

    @staticmethod
    def xls_export_cache_name(assessment):
        return 'animal-xls-assessment-{0}'.format(assessment.pk)

    @classmethod
    def flat_file_header(cls):
        return ['study',
                'study_url',
                'Study Primary Key',
                'experiment',
                'experiment_url',
                'animal_group',
                'animal_group_url',
                'endpoint_name',
                'endpoint_url',
                'data_type',
                'doses',
                'dose_units',
                'response_units',
                'primary_key',
                'low_dose',
                'NOAEL',
                'LOAEL',
                'FEL',
                'high_dose',
                'BMD model name',
                'BMDL',
                'BMD',
                'BMDU',
                'CSF',
                'dose_index',
                'dose',
                'n',
                'incidence',
                'response',
                'stdev',
                'percentControlMean',
                'percentControlLow',
                'percentControlHigh'
                ]

    @classmethod
    def get_flat_file(cls, queryset, output_format, dose):
        """
        Construct an export file of the selected subset of endpoints.
        """
        headers = Endpoint.flat_file_header()
        if output_format == "tsv":
            return build_tsv_file(headers, queryset, dose)
        else: # Excel by default
            sheet_name = 'bioassay'
            data_rows_func = Endpoint.build_excel_rows
            return build_excel_file(sheet_name, headers, queryset,
                                    data_rows_func, dose=dose)

    @staticmethod
    def build_excel_rows(ws, queryset, *args, **kwargs):
        """
        Custom method used to build individual excel rows in Excel worksheet
        """
        # write data
        def try_float(str):
            # attempt to coerce as float, else return string
            try:
                return float(str)
            except:
                return str

        i = 0
        dose = kwargs.get('dose', None)

        for endpoint in queryset:
            rows = endpoint.flat_file_row(dose)
            for row in rows:
                i+=1
                for j, val in enumerate(row):
                    ws.write(i, j, try_float(val))

    @staticmethod
    def endpoints_word_report(queryset):
        docx = HAWCdocx()
        docx.doc.add_heading("Example heading", 1)
        for endpoint in queryset:
            endpoint.docx_print(docx, 2)
        return docx

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
        return VARIANCE_NAME.get(self.variance_type, "N/A")

    def docx_print(self, report, heading_level):
        """
        Word report format for endpoint printing.
        """
        # define content
        title = u'Endpoint summary: {0}'.format(self.name)
        paras = (
            u'Endpoint summary, including dose-response table and BMDS outputs.',
            u'Created: {0}'.format(HAWCdocx.to_date_string(self.created)),
            u'Last Updated: {0}'.format(HAWCdocx.to_date_string(self.changed)),
            u'System: {0}'.format(self.system),
            u'Organ: {0}'.format(self.organ),
            u'Effect: {0}'.format(self.effect),
            u'Data location in reference: {0}'.format(self.data_location),
            u'Data available?: {0}'.format(self.data_reported),
            u'Data extracted?: {0}'.format(self.data_extracted),
            u'Data-values estimated?: {0}'.format(self.values_estimated),
            u'Response Units: {0}'.format(self.response_units),
            u'LOAEL: {0}'.format(self.get_LOAEL()),
            u'NOAEL: {0}'.format(self.get_NOAEL()),
            u'FEL: {0}'.format(self.get_FEL()),
            u'Monotonicity: {0}'.format(self.get_monotonicity_display()),
            u'Statistical Test: {0}'.format(self.statistical_test),
            u'Trend-value: {0}'.format(self.trend_value),
            u'Results notes: {0}'.format(self.results_notes),
            u'Endpoint notes: {0}'.format(self.endpoint_notes))

        # save endpoint-table
        doses = self.get_doses_json(json_encode=False)
        table_header = [('Dose (' + dose['units'] + ')') for dose in doses]
        if self.data_type == 'C':
            table_header.extend(['N', 'Response', self.variance_name])
        else:
            table_header.extend(['Incidence', 'N', r'% Incidence'])
        rows = [table_header]
        egs = self.get_endpoint_groups()
        for eg in egs:
            rows.append(eg.docx_print_row(self.data_type, doses))

        bmd_session = self.get_bmds_session()

        # print to document
        report.doc.add_heading(title, level=heading_level)
        for para in paras:
            report.doc.add_paragraph(para)

        tbl = report.doc.add_table(len(rows), len(rows[0]))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                tbl.cell(i, j).text = val

        report.doc.add_page_break()

        if bmd_session:
            bmd_session.docx_print(report, heading_level=heading_level+1)

    @staticmethod
    def d_responses(queryset, dose_pk):
        """
        Return a list of queryset responses with the specified dosing protocol
        """
        d_response_list = []
        for endpoint in queryset:
            d_response_list.append(endpoint.d_response(json_encode=False, dose_pk=dose_pk))
        return json.dumps(d_response_list, cls=HAWCDjangoJSONEncoder)

    def d_response(self, json_encode=True, dose_pk=None):
        """
        Javascript-object style format endpoint object. Contains all endpoint-groups,
        associated doses and dose-groups and BMD modeling results.
        """
        cache_name = 'endpoint-json-{pk}'.format(pk=self.pk)
        d = cache.get(cache_name)
        if d:
            logging.info('using cache: {cache_name}'.format(cache_name=cache_name))
        else:
            d = {}
            d['endpoint_type'] = 'bioassay'

            # study details
            d['study'] = self.animal_group.experiment.study.get_json(json_encode=False)

            # experiment details
            d['experiment'] = self.animal_group.experiment.__unicode__()
            d['experiment_url'] = self.animal_group.experiment.get_absolute_url()

            # animal group details
            d['animal_group'] = unicode(self.animal_group)
            d['animal_group_url'] = self.animal_group.get_absolute_url()
            d['species'] = unicode(self.animal_group.species)
            d['strain'] = unicode(self.animal_group.strain)
            d['sex'] = self.animal_group.get_sex_display()

            # endpoint details
            fields = ['pk', 'name', 'assessment_id',
                      'system', 'organ', 'effect',
                      'data_location', 'response_units', 'data_type', 'variance_type',
                      'variance_name', 'NOAEL', 'LOAEL', 'FEL',
                      'data_reported', 'data_extracted', 'values_estimated',
                      'dataset_increasing', 'individual_animal_data',
                      'statistical_test', 'trend_value', 'results_notes',
                      'endpoint_notes']
            for field in fields:
                d[field] = getattr(self, field)
            d['url'] = self.get_absolute_url()
            d['monotonicity'] = self.get_monotonicity_display()
            d['experiment_type'] = self.animal_group.experiment.get_type_display()
            d['doses'] = self.get_doses_json(json_encode=False)
            d['tags'] = list(self.effects.all().values('name', 'slug'))
            d['additional_fields'] = json.loads(self.additional_fields)

            # endpoint-group details
            egs = self.get_endpoint_groups()
            d['dr'] = list(egs.values('pk', 'dose_group_id', 'n', 'incidence',
                                       'response', 'variance', 'significant',
                                       'significance_level'))
            for i, eg in enumerate(d['dr']):
                eg['stdev'] = EndpointGroup.stdev(self.variance_type, eg['variance'], eg['n'])
            EndpointGroup.percentControl(self.data_type, d['dr'])

            # individual animal data
            if self.individual_animal_data:
                individuals = EndpointGroup.objects.filter(endpoint=self.pk).select_related('endpoint_group__individual_data').values('dose_group_id', 'individual_data__response')
                for i, dr in enumerate(d['dr']):
                    dr['individual_responses'] = [v['individual_data__response'] for v in individuals if v['dose_group_id'] == dr['dose_group_id']]

            # BMD data
            try:
                d['BMD'] = self.get_bmds_session().get_selected_model(json_encode=False)
            except:
                d['BMD'] = None

            if type(d['BMD']) is not dict: d['BMD'] = None

            logging.info('setting cache: {cache_name}'.format(cache_name=cache_name))
            cache.set(cache_name, d)

        # Not cached without refactoring because this may depend on the dose
        # primary key. TODO: Instead, grab all BMD doses for each units type,
        # and then grab the correct one via javascript
        try:
            if dose_pk:
                dose_index = None
                for i, dose_value in enumerate(d['doses']):
                    if (dose_value['units_id'] == dose_pk):
                        dose_index = i
                        break
                if dose_index is None:
                    raise Exception('Dose units not found')
            else:
                dose_index = 0  # by default, set dose equal to first dose value
            d['dose_units'] = d['doses'][dose_index]['units']
            d['dose_units_index'] = dose_index
            d['dose_units_id'] = d['doses'][dose_index]['units_id']
            for i, dose in enumerate(d['doses'][dose_index]['values']):
                d['dr'][i]['dose'] = dose
        except:
            d['warnings'] = 'doses undefined'

        #JSON-encoding differences
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    def d_response_ufs(self, json_encode=True, dose_pk=None):
        """
        Javascript-object style format endpoint object, but also includes
        uncertainty factors associated with object.
        """
        d = self.d_response(json_encode=False, dose_pk=dose_pk)
        ufs = UncertaintyFactorEndpoint.objects.filter(endpoint=self.pk)
        d['ufs'] = []
        for uf in ufs:
            d['ufs'].append(uf.get_dictionary())
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

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

    def get_LOAEL(self):
        """
        Return LOAEL based on first-dose type or None.
        """
        if not hasattr(self, 'doses'):
            self.get_doses_json()
        try:
            return float(self.doses[0]['values'][self.LOAEL])
        except:
            return None

    def get_NOAEL(self):
        """
        Return NOAEL based on first-dose type or None.
        """
        if not hasattr(self, 'doses'):
            self.get_doses_json()
        try:
            return float(self.doses[0]['values'][self.NOAEL])
        except:
            return None

    def get_FEL(self):
        """
        Return FEL based on first-dose type or None.
        """
        if not hasattr(self, 'doses'):
            self.get_doses_json()
        try:
            return float(self.doses[0]['values'][self.FEL])
        except:
            return None

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
            return BMD_session.objects.filter(endpoint=self.pk).latest('updated')
        except:
            return None

    @staticmethod
    def detailed_excel_export(queryset, assessment):
        """
        Full XLS data export for the animal bioassay data. Does not include any
        aggregation information, uncertainty-values, or reference values.
        """
        cache_name = Endpoint.xls_export_cache_name(assessment)
        excel = cache.get(cache_name)
        if excel:
            logging.info('using cache: {name}'.format(name=cache_name))
        else:
            sheet_name = 'ani'
            doses = DoseUnits.doses_in_assessment(assessment)
            headers = Endpoint.detailed_excel_export_header(doses)
            data_rows_func = Endpoint.build_export_rows
            excel = build_excel_file(sheet_name, headers, queryset, data_rows_func, doses=doses)
            logging.info('setting cache: {name}'.format(name=cache_name))
            cache.set(cache_name, excel)
        return excel

    @staticmethod
    def excel_export_detail(dic, isHeader):
        blacklist = ["endpoint-NOAEL", "endpoint-LOAEL", "endpoint-FEL"]
        return excel_export_detail(dic, isHeader, blacklist)

    @staticmethod
    def detailed_excel_export_header(doses):
        # build export header column names for full export
        Study = models.get_model('study', 'Study')
        lst = []
        # grab any endpoint for this case; in case the current assessment has no animal endpoints
        endpoint = Endpoint.objects.all()[0]
        if endpoint:
            d = endpoint.getDict(target=True)
            lst.extend(Study.excel_export_detail(d['_study'], True))
            lst.extend(Experiment.excel_export_detail(d['_experiment'], True))
            lst.extend(AnimalGroup.excel_export_detail(d['_animal_group'], True))
            lst.extend(AnimalGroup.excel_export_detail(d['_animal_group']['_species'], True))
            lst.extend(AnimalGroup.excel_export_detail(d['_animal_group']['_strain'], True))
            lst.extend(AnimalGroup.excel_export_detail(d['_animal_group']['_dosing_regime'], True))
            lst.extend(['doses-' + dose for dose in doses])
            lst.extend(Endpoint.excel_export_detail(d, True))
            if len(d['_endpoint_groups'])>0:
                lst.extend(EndpointGroup.excel_export_detail(d['_endpoint_groups'][0], True, d))
        return lst

    @staticmethod
    def build_export_rows(ws, queryset, *args, **kwargs):
        doses = kwargs.get('doses', [])
        # build export data rows for full-export
        def try_float(val):
            if type(val) is bool:
                return val
            try:
                return float(val)
            except:
                return val

        Study = models.get_model('study', 'Study')
        r = 0
        for endpoint in queryset:
            d = endpoint.getDict(target=True)
            lst = []
            lst.extend(Study.excel_export_detail(d['_study'], False))
            lst.extend(Experiment.excel_export_detail(d['_experiment'], False))
            lst.extend(AnimalGroup.excel_export_detail(d['_animal_group'], False))
            lst.extend(AnimalGroup.excel_export_detail(d['_animal_group']['_species'], False))
            lst.extend(AnimalGroup.excel_export_detail(d['_animal_group']['_strain'], False))
            lst.extend(AnimalGroup.excel_export_detail(d['_animal_group']['_dosing_regime'], False))
            dose_idx = len(lst)
            lst.extend([None]*len(doses))
            lst.extend(Endpoint.excel_export_detail(d, False))

            # build a row for each endpoint group
            for i, eg in enumerate(d['_endpoint_groups']):
                r+=1
                new_fields = list(lst)  # clone
                # write endpoint-group details
                new_fields.extend(EndpointGroup.excel_export_detail(eg, False, d))

                # write dose-details
                for j, dose in enumerate(doses):
                    try:
                        new_fields[dose_idx+j] = d['_animal_group']['_dosing_regime']['_doses'][dose][i]
                    except KeyError:
                        pass

                for c, val in enumerate(new_fields):
                    ws.write(r, c, try_float(val))


class EndpointGroup(models.Model):
    endpoint = models.ForeignKey(
        Endpoint,
        related_name='endpoint_group')
    dose_group_id = models.IntegerField(
        blank=False)
    n = models.PositiveSmallIntegerField(
        blank=False,
        validators=[MinValueValidator(0)])
    incidence = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)])
    response = models.DecimalField(
        max_digits=50,
        decimal_places=25,
        blank=True,
        null=True)
    variance = models.DecimalField(
        max_digits=50,
        decimal_places=25,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)])
    significant = models.BooleanField(
        default=False,
        verbose_name="Statistically significant from control")
    significance_level = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name="Statistical significance level")

    class Meta:
        ordering = ('endpoint', 'dose_group_id')

    def clean(self):
        if self.endpoint.data_type == 'C':
            if self.variance is None:
                raise ValidationError('Variance must be numeric')
            if self.response is None:
                raise ValidationError('Response must be numeric')
        else:
            if self.incidence is None:
                raise ValidationError('Incidence must be numeric')

        self.significant = (self.significance_level > 0)

    def docx_print_row(self, data_type, doses):
        """
        Print Word representation of self, for insertion into a table.
        """
        try:
            # try this first, should work endpoint-groups = dose-groups
            row = [str(float(dose['values'][self.dose_group_id])) for dose in doses]
        except:
            # do this instead if there are differences between dose-groups
            row = []
            for dose in doses:
                try:
                    row.append(str(float(dose['values'][self.dose_group_id])))
                except:
                    row.append('Error')

        if data_type == 'C':
            row.extend([str(float(self.n)),
                        str(float(self.response)),
                        str(float(self.variance))])
        else:
            row.extend([str(float(self.n)),
                        str(float(self.incidence)),
                        str(float(100.*(self.incidence/self.n)))])
        return row

    @staticmethod
    def stdev(variance_type, variance, n):
        # calculate stdev given re
        if variance_type == 1:
            return variance
        elif variance_type == 2:
            return float(variance) * math.sqrt(n)
        else:
            return None

    def getStdev(self, variance_type=None):
        """ Return the stdev of an endpoint-group, given the variance type. """

        # don't hit DB unless we need to
        if variance_type is None:
            variance_type = self.endpoint.variance_type

        return EndpointGroup.stdev(variance_type, self.variance, self.n)

    @staticmethod
    def percentControl(data_type, egs):
        #
        # Expects a dictionary of endpoint groups and the endpoint data-type.
        #
        # Returns the confidence interval for a population mean, assuming a
        # normal distribution. Requires continuous data with a stdev.
        #
        # Appends results to the dictionary for each endpoint-group.
        #
        for eg in egs:
            eg['percentControlMean'] = None
            eg['percentControlLow'] = None
            eg['percentControlHigh'] = None
            if data_type == "C":
                sqrt_n = math.sqrt(eg['n'])
                resp_control = float(egs[0]['response'])
                if ((sqrt_n != 0) and (resp_control != 0)):
                    eg['percentControlMean'] =  float(eg['response']) / resp_control * 100.
                    ci = (1.96 * float(eg['stdev']) / sqrt_n) / resp_control * 100.
                    eg['percentControlLow']  = (eg['percentControlMean'] - ci)
                    eg['percentControlHigh'] = (eg['percentControlMean'] + ci)

    def save(self, *args, **kwargs):
        super(EndpointGroup, self).save(*args, **kwargs)
        Endpoint.d_response_delete_cache([self.endpoint.pk])

    def getDict(self):
        """
        Return flat-dictionary of EndpointGroup.
        """
        return OrderedDict((
                ("endpoint_group-pk", self.pk),
                ("endpoint_group-dose_group_id", self.dose_group_id),
                ("endpoint_group-n", self.n),
                ("endpoint_group-incidence", self.incidence),
                ("endpoint_group-response", self.response),
                ("endpoint_group-variance", self.variance),
                ("endpoint_group-significant", self.significant),
                ("endpoint_group-significance_level", self.significance_level)
        ))

    @staticmethod
    def excel_export_detail(dic, isHeader, endpoint_dic):
        lst = excel_export_detail(dic, isHeader)

        if isHeader:
            lst.extend(["endpoint_group-NOAEL",
                         "endpoint_group-LOAEL",
                         "endpoint_group-FEL"])
        else:
            lst.extend([
                endpoint_dic["endpoint-NOAEL"] == dic["endpoint_group-dose_group_id"],
                endpoint_dic["endpoint-LOAEL"] == dic["endpoint_group-dose_group_id"],
                endpoint_dic["endpoint-FEL"]   == dic["endpoint_group-dose_group_id"]
            ])

        return lst


class IndividualAnimal(models.Model):
    endpoint_group = models.ForeignKey(
        EndpointGroup,
        related_name='individual_data')
    response = models.DecimalField(
        max_digits=50,
        decimal_places=25)

    def save(self, *args, **kwargs):
        super(IndividualAnimal, self).save(*args, **kwargs)
        #todo: move to model view to prevent redundancies
        Endpoint.d_response_delete_cache([self.endpoint_group.endpoint.pk])


UF_TYPE_CHOICES = (('UFA', 'Interspecies uncertainty'),
                   ('UFH', 'Intraspecies variability'),
                   ('UFS', 'Subchronic to chronic extrapolation'),
                   ('UFL', 'Use of a LOAEL in absence of a NOAEL'),
                   ('UFD', 'Database incomplete'),
                   ('UFO', 'Other'))


class UncertaintyFactorAbstract(models.Model):
    uf_type = models.CharField(
        max_length=3,
        choices=UF_TYPE_CHOICES,
        verbose_name="Uncertainty Value Type")
    value = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=10,
        help_text="Note that 3*3=10 for all uncertainty value calculations; "
                  "therefore specifying 3.33 is not required.",
        validators=[MinValueValidator(1)])
    description = models.TextField(
        blank=True,
        verbose_name='Justification')
    created = models.DateTimeField(
        auto_now_add=True)
    updated = models.DateTimeField(
        auto_now=True)  # standardize changed to updated

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.get_uf_type_display()

    @property
    def uf_type_pretty(self):
        return self.get_uf_type_display()

    def get_absolute_url(self):
        return reverse('animal:uf_detail', args=[self.pk])

    def get_dictionary(self):
        d = {}
        fields = ['pk', 'uf_type', 'value', 'description', 'uf_type_pretty']
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

    def save(self, *args, **kwargs):
        super(UncertaintyFactorEndpoint, self).save(*args, **kwargs)
        # cache deletion not required because UFs not-saved with this version of EndpointGroup
        # cache.delete('endpoint-json-{pk}'.format(pk=self.endpoint.endpoint_group.pk))

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


AGGREGATION_TYPE_CHOICES = (('E', 'Evidence'),
                            ('M', 'Mode-of-action'),
                            ('CD', 'Candidate Reference Values'))


class Aggregation(models.Model):
    """
    Aggregation of endpoints
    """
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
        # get all the endpoints with the proper dose-type
        endpoints = []
        for endpoint in self.endpoints.all().select_related('animal_group', 'animal_group__dosing_regime'):
            endpoints.append(endpoint.d_response(json_encode=False, dose_pk=self.dose_units.pk))
        if json_encode:
            return json.dumps(endpoints, cls=HAWCDjangoJSONEncoder)
        return endpoints

    def get_endpoints_ufs_json(self, json_encode=True):
        # get all the endpoints with the proper dose-type and uncertainty factors
        endpoints = []
        for endpoint in self.endpoints.all().select_related('animal_group', 'animal_group__dosing_regime'):
            endpoints.append(endpoint.d_response_ufs(json_encode=False, dose_pk=self.dose_units.pk))
        if json_encode:
            return json.dumps(endpoints, cls=HAWCDjangoJSONEncoder)
        return endpoints

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
                    fields['aggregation_type'], AGGREGATION_TYPE_CHOICES)
            fields['changed_by'] = version.revision.user.get_full_name()
            fields['updated'] = version.revision.date_created
            fields['endpoints'] = get_endpoints(fields['endpoints'])
            fields.pop('assessment')
            versions_json.append(fields)
        return json.dumps(versions_json, cls=HAWCDjangoJSONEncoder)

    def get_json(self, json_encode=True):
        d = {"endpoints":[],
             "url": self.get_absolute_url()}
        for field in ['pk', 'name']:
            d[field] = getattr(self, field)
        for endpoint in self.endpoints.all():
            d["endpoints"].append(endpoint.d_response(json_encode=False,
                                  dose_pk=self.dose_units.pk))
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


REFERENCE_VALUE_CHOICES = ((1, 'Oral RfD'),
                           (2, 'Inhalation RfD'),
                           (3, 'Oral CSF'),
                           (4, 'Inhalation CSF'))


class ReferenceValue(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='reference_values')
    point_of_departure = models.DecimalField(
        max_digits=50,
        decimal_places=25,
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
    aggregate_uf = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True)
    reference_value = models.DecimalField(
        max_digits=50,
        decimal_places=25,
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    changed = models.DateTimeField(
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
        return (float(self.point_of_departure) / self.calculate_total_uncertainty_value(ufs_list))

    def calculate_total_uncertainty_value(self, ufs_list=None):
        # in RfD math, 3*3=10.

        def approx_equal(x, y, tolerance=0.001):
            return abs(x-y) <= 0.5 * tolerance * (x + y)

        aggregate_uf = 1.
        threes = 0

        if ufs_list is None:
            ufs_list = list(self.ufs.values_list('value', flat=True))
            ufs_list = [float(v) for v in ufs_list]

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
        pk_exclusion = {}
        if self.pk:
            pk_exclusion['pk'] = self.pk
        if ReferenceValue.objects.filter(assessment=self.assessment,
                                         type=self.type,
                                         units=self.units).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- reference value factor type already exists for this combination of assessment, reference-type, and units.')

    def get_json(self, json_encode=True):
        fields = ['pk', 'point_of_departure', 'justification', 'created', 'changed']
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
            ufs.append(float(form.cleaned_data['value']))
        self.aggregate_uf = self.calculate_total_uncertainty_value(ufs)
        self.reference_value = self.calculate_reference_value(ufs)
        self.save()


reversion.register(Species)
reversion.register(Strain)
reversion.register(Experiment)
reversion.register(AnimalGroup)
reversion.register(GenerationalAnimalGroup)
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
