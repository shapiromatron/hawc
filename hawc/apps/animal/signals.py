from django.db import transaction
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


@receiver(post_save, sender=models.DosingRegime)
def change_num_dg(sender, instance, **kwargs):
    # Ensure number endpoint-groups == dose-groups;

    # get endpoints associated with this dosing-regime
    endpoints = models.Endpoint.objects.filter(
        animal_group_id__in=models.AnimalGroup.objects.filter(dosing_regime=instance),
        data_extracted=True,
    )

    # no changes required if we have no endpoints
    if endpoints.count() == 0:
        return

    # get dose-ids
    dose_group_ids = sorted(set(instance.doses.all().values_list("dose_group_id", flat=True)))

    # create endpoint-groups, as needed
    creates = []
    for dg_id in dose_group_ids:
        for ep in endpoints.exclude(groups__dose_group_id=dg_id):
            creates.append(models.EndpointGroup(endpoint_id=ep.id, dose_group_id=dg_id))

    # delete endpoint-groups without a dose-group, as needed
    deletes = models.EndpointGroup.objects.filter(endpoint__in=endpoints).exclude(
        dose_group_id__in=dose_group_ids
    )

    with transaction.atomic():
        models.EndpointGroup.objects.bulk_create(creates)
        deletes.delete()
