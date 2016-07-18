import collections
import json
import os

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import now

from utils.models import get_crumbs

from .bmds_monkeypatch import bmds


BMDS_CHOICES = (
    ('2.30', 'Version 2.30'),
    ('2.31', 'Version 2.31'),
    ('2.40', 'Version 2.40'),
    ('2.60', 'Version 2.60'),
    ('2.601', 'Version 2.601'),
)

LOGIC_BIN_CHOICES = (
    (0, 'Warning (no change)'),
    (1, 'Questionable'),
    (2, 'Not Viable'),
)


class BMDSession(models.Model):
    endpoint = models.ForeignKey(
        'animal.Endpoint',
        related_name='bmd_sessions')
    dose_units = models.ForeignKey(
        'assessment.DoseUnits',
        related_name='bmd_sessions')
    version = models.CharField(
        max_length=10,
        choices=BMDS_CHOICES)
    bmrs = JSONField(
        default=dict)
    date_executed = models.DateTimeField(
        null=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        get_latest_by = "last_updated"
        ordering = ('-last_updated', )

    def __unicode__(self):
        return 'BMD session'

    def get_assessment(self):
        return self.endpoint.get_assessment()

    def get_crumbs(self):
        return get_crumbs(self, self.endpoint)

    def get_absolute_url(self):
        return reverse_lazy('bmd:session_detail', args=[self.id])

    def get_update_url(self):
        return reverse_lazy('bmd:session_update', args=[self.id])

    def get_delete_url(self):
        return reverse_lazy('bmd:session_delete', args=[self.id])

    def get_api_url(self):
        return reverse_lazy('bmd:api:bmd_session-detail', args=[self.id])

    def get_execute_url(self):
        return reverse_lazy('bmd:api:bmd_session-execute', args=[self.id])

    def get_execute_status_url(self):
        return reverse_lazy('bmd:api:bmd_session-execute-status', args=[self.id])

    def get_selected_model_url(self):
        return reverse_lazy('bmd:api:bmd_session-selected-model', args=[self.id])

    @classmethod
    def create_new(cls, endpoint):
        dose_units = endpoint.get_doses_json(json_encode=False)[0]['id']
        version = endpoint.assessment.BMD_Settings.version
        return cls.objects.create(
            endpoint_id=endpoint.id,
            dose_units_id=dose_units,
            version=version)

    @property
    def is_finished(self):
        return self.date_executed is not None

    def execute(self):
        self.date_executed = now()
        self.save()
        session = self.get_session(withModels=True)
        session.execute()

    def get_endpoint_dataset(self):
        ds = self.endpoint.d_response(json_encode=False)
        doses = [
            dose['dose']
            for dose in ds['animal_group']['dosing_regime']['doses']
            if dose['dose_units']['id'] == self.dose_units_id
        ]
        grps = ds['groups']
        if self.endpoint.data_type == 'C':
            return bmds.ContinuousDataset(
                doses=doses,
                ns=[d['n'] for d in grps],
                responses=[d['response'] for d in grps],
                stdevs=[d['stdev'] for d in grps],
            )
        else:
            return bmds.DichotomousDataset(
                doses=doses,
                ns=[d['n'] for d in grps],
                incidences=[d['incidence'] for d in grps],
            )

    def get_bmr_overrides(self, session, index):
        # convert bmr overrides from GUI to modeling version
        bmr = self.bmrs[index]
        type_ = bmds.constants.BMR_CROSSWALK[session.dtype][bmr['type']]
        return {
            'bmr_type': type_,
            'bmr': bmr['value'],
            'confidence_level': bmr['confidence_level'],
        }

    def get_session(self, withModels=False):

        session = getattr(self, '_session', None)

        if session is None:
            version = self.endpoint.assessment.BMD_Settings.version
            Session = bmds.get_session(version)
            dataset = self.get_endpoint_dataset()
            session = Session(
                self.endpoint.data_type,
                dataset=dataset
            )
            self._session = session

        if withModels and not session.has_models:
            for model in self.models.all():
                session.add_model(
                    model.name,
                    overrides=model.overrides
                )

        return session

    def get_model_options(self):
        return self.get_session().get_model_options()

    def get_bmr_options(self):
        return self.get_session().get_bmr_options()


class BMDModel(models.Model):
    session = models.ForeignKey(
        BMDSession,
        related_name='models')
    model_id = models.PositiveSmallIntegerField()
    bmr_id = models.PositiveSmallIntegerField()
    name = models.CharField(
        max_length=25)
    overrides = JSONField(
        default=dict)
    date_executed = models.DateTimeField(
        null=True)
    execution_error = models.BooleanField(
        default=False)
    dfile = models.TextField(
        blank=True)  # bmds raw output file
    plot = models.ImageField(
        upload_to='bmds_plot',
        blank=True)
    outputs = JSONField(
        default=dict)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        get_latest_by = "created"
        ordering = ('model_id', )

    def get_assessment(self):
        return self.session.get_assessment()


class SelectedModel(models.Model):
    endpoint = models.OneToOneField(
        'animal.Endpoint',
        related_name='bmd_model')
    model = models.ForeignKey(
        BMDModel,
        null=True)
    notes = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        get_latest_by = "created"

    @classmethod
    def save_new(cls, endpoint):
        cls.objects.create(endpoint=endpoint)

    def change_selection(self, endpoint=None, notes=''):
        self.endpoint = endpoint
        self.notes = notes
        self.save()

    def get_assessment(self):
        return self.endpoint.get_assessment()


class BMD_Assessment_Settings(models.Model):
    assessment = models.OneToOneField(
        'assessment.Assessment',
        related_name='BMD_Settings')
    version = models.CharField(
        max_length=10,
        choices=BMDS_CHOICES,
        default=BMDS_CHOICES[-1][0])
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "BMD assessment settings"

    def __unicode__(self):
        return self.assessment.__unicode__() + ' BMD settings'

    def get_absolute_url(self):
        return reverse_lazy('bmd:assess_settings_detail',
                            args=[self.assessment.pk])

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_default(cls, assessment):
        cls.objects.create(assessment=assessment)


class LogicField(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='BMD_Logic_Fields',
        editable=False)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)
    logic_id = models.PositiveSmallIntegerField(
        editable=False)
    name = models.CharField(
        max_length=30,
        editable=False)
    function_name = models.CharField(
        max_length=25,
        editable=False)
    description = models.TextField(
        editable=False)
    failure_bin = models.PositiveSmallIntegerField(
        choices=LOGIC_BIN_CHOICES,
        blank=False,
        help_text="If the test fails, select the model-bin should the model be placed into.")  # noqa
    threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="If a threshold is required for the test, threshold can be specified to non-default.")  # noqa
    continuous_on = models.BooleanField(
        default=True,
        verbose_name="Continuous Datasets")
    dichotomous_on = models.BooleanField(
        default=True,
        verbose_name="Dichotomous Datasets")
    cancer_dichotomous_on = models.BooleanField(
        default=True,
        verbose_name="Cancer Dichotomous Datasets")

    class Meta:
        ordering = ['logic_id']

    def __unicode__(self):
        return self.description

    def get_absolute_url(self):
        return reverse_lazy('bmd:assess_settings_detail',
                            args=[self.assessment_id])

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_defaults(cls, assessment):
        """
        Build default BMD decision logic.
        """
        fn = os.path.join(
            settings.PROJECT_PATH,
            'bmd/fixtures/logic.json'
        )
        with open(fn, 'r') as f:
            text = json.loads(
                f.read(),
                object_pairs_hook=collections.OrderedDict)

        objects = [
            cls(assessment_id=assessment.id, logic_id=i, **obj)
            for i, obj in enumerate(text['objects'])
        ]
        cls.objects.bulk_create(objects)
