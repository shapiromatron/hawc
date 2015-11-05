from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.MetaProtocol)
@receiver(pre_delete, sender=models.MetaProtocol)
@receiver(post_save, sender=models.MetaResult)
@receiver(pre_delete, sender=models.MetaResult)
@receiver(post_save, sender=models.SingleResult)
@receiver(pre_delete, sender=models.SingleResult)
def invalidate_meta_result_cache(sender, instance, **kwargs):
    instance_type = type(instance)
    filters = {}
    if instance_type is models.MetaProtocol:
        filters["protocol"] = instance.id
    elif instance_type is models.MetaResult:
        ids = [instance.id]
    elif instance_type is models.SingleResult:
        ids = [instance.meta_result_id]

    if len(filters) > 0:
        ids = models.MetaResult.objects\
            .filter(**filters)\
            .values_list('id', flat=True)

    models.MetaResult.delete_caches(ids)
