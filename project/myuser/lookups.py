from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class HAWCUserLookup(ModelLookup):
    model = models.HAWCUser
    search_fields = (
        'first_name__icontains',
        'last_name__icontains',
        'email__icontains',
    )
    filters = {'is_active': True, }

registry.register(HAWCUserLookup)
