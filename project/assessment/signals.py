import logging

from django.db.models.loading import get_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.Assessment)
def default_configuration(sender, instance, created, **kwargs):
    """
    Created default assessment settings when a new assessment instance
    is created.
    """
    if created:

        logging.info("Creating default literature inclusion/exclusion tags")
        get_model('lit', 'ReferenceFilterTag').build_default(instance)
        get_model('lit', 'Search').build_default(instance)

        logging.info("Creating default settings for study-quality criteria")
        get_model('study', 'StudyQualityDomain').build_default(instance)

        logging.info("Creating new BMD settings assessment creation")
        get_model('bmd', 'LogicField').build_defaults(instance)
        get_model('bmd', 'BMD_Assessment_Settings')(assessment=instance).save()

        logging.info("Creating default summary text")
        get_model('summary', 'SummaryText').build_default(instance)

        logging.info("Building default comment settings")
        get_model('comments', 'CommentSettings')(assessment=instance).save()

        logging.info("Building in-vitro endpoint category-root")
        get_model('invitro', 'IVEndpointCategory').create_root(assessment_id=instance.pk)
