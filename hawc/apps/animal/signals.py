from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.Experiment)
@receiver(pre_delete, sender=models.Experiment)
@receiver(post_save, sender=models.AnimalGroup)
@receiver(pre_delete, sender=models.AnimalGroup)
@receiver(post_save, sender=models.DosingRegime)
@receiver(pre_delete, sender=models.DosingRegime)
@receiver(post_save, sender=models.Endpoint)
@receiver(pre_delete, sender=models.Endpoint)
@receiver(post_save, sender=models.EndpointGroup)
@receiver(pre_delete, sender=models.EndpointGroup)
def invalidate_endpoint_cache(sender, instance, **kwargs):
    instance_type = type(instance)
    filters = {}
    if instance_type is models.Experiment:
        filters["animal_group__experiment"] = instance.id
    elif instance_type is models.AnimalGroup:
        filters["animal_group"] = instance.id
    elif instance_type is models.DosingRegime:
        filters["animal_group__dosing_regime"] = instance.id
    elif instance_type is models.Endpoint:
        ids = [instance.id]
    elif instance_type is models.EndpointGroup:
        ids = [instance.endpoint_id]

    if len(filters) > 0:
        ids = models.Endpoint.objects.filter(**filters).values_list("id", flat=True)

    models.Endpoint.delete_caches(ids)


@receiver(post_save, sender=models.Endpoint)
@receiver(post_save, sender=models.DosingRegime)
def sync_dose_groups(sender, instance, **kwargs):
    instance.sync_dose_groups()
