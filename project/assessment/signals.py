import logging

from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

import models


@receiver(post_save, sender=models.Assessment)
def default_configuration(sender, instance, created, **kwargs):
    """
    Created default assessment settings when a new assessment instance
    is created.
    """
    if created:

        logging.info("Creating default literature inclusion/exclusion tags")
        apps.get_model('lit', 'ReferenceFilterTag').build_default(instance)
        apps.get_model('lit', 'Search').build_default(instance)

        logging.info("Creating default settings for risk of bias criteria")
        apps.get_model('riskofbias', 'RiskOfBiasDomain').build_default(instance)
        apps.get_model('riskofbias', 'RiskOfBiasAssessment').build_default(instance)

        logging.info("Creating new BMD settings assessment creation")
        apps.get_model('bmd', 'LogicField').build_defaults(instance)
        apps.get_model('bmd', 'BMD_Assessment_Settings')(assessment=instance).save()

        logging.info("Creating default summary text")
        apps.get_model('summary', 'SummaryText').build_default(instance)

        logging.info("Building default comment settings")
        apps.get_model('comments', 'CommentSettings')(assessment=instance).save()

        logging.info("Building in-vitro endpoint category-root")
        apps.get_model('invitro', 'IVEndpointCategory').create_root(assessment_id=instance.pk)
