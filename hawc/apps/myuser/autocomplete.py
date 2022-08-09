from django.db.models import Q

from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class UserAutocomplete(BaseAutocomplete):
    model = models.HAWCUser
    search_fields = ["first_name", "last_name", "email"]

    @classmethod
    def get_base_queryset(cls, filters: dict = None):
        qs = super().get_base_queryset(filters)
        # if assessment id is provided, return team member or higher
        if (assessment_id := filters.get("assessment_id")) is not None:
            qs = qs.filter(
                Q(assessment_pms__id=assessment_id) | Q(assessment_teams__id=assessment_id)
            ).distinct()
        return qs

    def get_queryset(self):
        # only get active user choices
        return super().get_queryset().filter(is_active=True)
