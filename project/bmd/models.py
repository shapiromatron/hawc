import collections
import json
import logging
import os
import random
import string

from django.db import models
from django.conf import settings
from django.core.files import File
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse


BMDS_CHOICES = (
    ('2.30', 'Version 2.30'),
    ('2.31', 'Version 2.31'),
    ('2.40', 'Version 2.40'),
)

LOGIC_BIN_CHOICES = (
    (0, 'Warning (no change)'),
    (1, 'Questionable'),
    (2, 'Not Viable'),
)


class BMD_Assessment_Settings(models.Model):
    assessment = models.OneToOneField(
        'assessment.Assessment',
        related_name='BMD_Settings')
    BMDS_version = models.CharField(
        max_length=10,
        choices=BMDS_CHOICES,
        default=max(BMDS_CHOICES)[0])
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "BMD assessment settings"

    def __unicode__(self):
        return self.assessment.__unicode__() + ' BMD settings'

    def get_absolute_url(self):
        return reverse('bmd:assess_settings_detail', args=[self.assessment.pk])

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
        return reverse('bmd:assess_settings_detail', args=[self.assessment_id])

    def webpage_return(self, endpoint_data_type, json=False):
        outputs = {
            'last_updated': self.last_updated,
            'logic_id': self.logic_id,
            'name': self.name,
            'function_name': self.function_name,
            'description': self.description,
            'failure_bin': self.failure_bin,
            'threshold': self.threshold,
            'test_on': self.datatype_inclusion(endpoint_data_type)
        }
        return json.dumps(outputs, cls=DjangoJSONEncoder) if json else outputs

    def datatype_inclusion(self, endpoint_data_type):
        crosswalk = {
            'C': self.continuous_on,
            'D': self.dichotomous_on,
            'DC': self.cancer_dichotomous_on
        }
        try:
            return crosswalk[endpoint_data_type]
        except:
            return False

    def get_assessment(self):
        return self.assessment

    @classmethod
    def website_list_return(cls, objs, endpoint_data_type, json=False):
        logics = []
        for obj in objs:
            logics.append(obj.webpage_return(endpoint_data_type, False))
        return json.dumps(logics, cls=DjangoJSONEncoder) if json else logics

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
