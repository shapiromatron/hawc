from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.StudyPopulation)
@receiver(pre_delete, sender=models.StudyPopulation)
@receiver(post_save, sender=models.ComparisonSet)
@receiver(pre_delete, sender=models.ComparisonSet)
@receiver(post_save, sender=models.Exposure)
@receiver(pre_delete, sender=models.Exposure)
@receiver(post_save, sender=models.Group)
@receiver(pre_delete, sender=models.Group)
@receiver(post_save, sender=models.Outcome)
@receiver(pre_delete, sender=models.Outcome)
@receiver(post_save, sender=models.Result)
@receiver(pre_delete, sender=models.Result)
@receiver(post_save, sender=models.GroupResult)
@receiver(pre_delete, sender=models.GroupResult)
def invalidate_outcome_cache(sender, instance, **kwargs):
    ids = []
    instance_type = type(instance)
    filters = {}
    if instance_type is models.StudyPopulation:
        filters["study_population_id"] = instance.id
    elif instance_type is models.ComparisonSet:
        filters["results__comparison_set_id"] = instance.id
    elif instance_type is models.Exposure:
        filters["results__comparison_set__exposure_id"] = instance.id
    elif instance_type is models.Group:
        filters["results__comparison_set__groups"] = instance.id
    elif instance_type is models.Outcome:
        ids = [instance.id]
    elif instance_type is models.Result:
        ids = [instance.outcome_id]
    elif instance_type is models.GroupResult:
        ids = [instance.result.outcome_id]

    if len(filters) > 0:
        ids = models.Outcome.objects.filter(**filters).values_list('id', flat=True)

    models.Outcome.delete_caches(ids)
