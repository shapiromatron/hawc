import operator

from django.db.models import Q
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


class AssessmentTeamMemberOrHigherLookup(HAWCUserLookup):

    def get_query(self, request, term):
        try:
            id_ = int(request.GET.get('related', -1))
        except ValueError:
            id_ = -1
        search_fields = [
            Q(**{field: term})
            for field in self.search_fields
        ]
        return self.model.objects.filter(
            Q(**{'assessment_pms__id': id_}) |
            Q(**{'assessment_teams__id': id_}) &
            reduce(operator.or_, search_fields)
        ).distinct()

registry.register(HAWCUserLookup)
registry.register(AssessmentTeamMemberOrHigherLookup)
