from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.IVChemical)
@receiver(pre_delete, sender=models.IVChemical)
@receiver(post_save, sender=models.IVCellType)
@receiver(pre_delete, sender=models.IVCellType)
@receiver(post_save, sender=models.IVExperiment)
@receiver(pre_delete, sender=models.IVExperiment)
@receiver(post_save, sender=models.IVEndpoint)
@receiver(pre_delete, sender=models.IVEndpoint)
@receiver(post_save, sender=models.IVEndpointGroup)
@receiver(pre_delete, sender=models.IVEndpointGroup)
@receiver(post_save, sender=models.IVBenchmark)
@receiver(pre_delete, sender=models.IVBenchmark)
def invalidate_endpoint_cache(sender, instance, **kwargs):
    instance_type = type(instance)
    filters = {}

    if instance_type is models.IVChemical:
        filters['chemical_id'] = instance.id
    elif instance_type is models.IVCellType:
        filters['experiment__cell_type_id'] = instance.id
    elif instance_type is models.IVExperiment:
        filters['experiment_id'] = instance.id
    elif instance_type is models.IVEndpoint:
        ids = [instance.id]
    elif instance_type is models.IVEndpointGroup:
        ids = [instance.id]
    elif instance_type is models.IVBenchmark:
        ids = [instance.endpoint_id]

    if len(filters) > 0:
        ids = models.IVEndpoint.objects\
            .filter(**filters)\
            .values_list('id', flat=True)

    models.IVEndpoint.delete_caches(ids)
