from rest_framework import filters

from .helper import get_assessment_from_query


class InAssessmentFilter(filters.BaseFilterBackend):
    """
    Filter objects which are in a particular assessment.
    """

    default_list_actions = ["list"]

    def filter_queryset(self, request, queryset, view):
        list_actions = getattr(view, "list_actions", self.default_list_actions)
        if view.action not in list_actions:
            return queryset

        if not hasattr(view, "assessment"):
            view.assessment = get_assessment_from_query(request)

        if not view.assessment_filter_args:
            raise ValueError("ViewSet requires the `assessment_filter_args` argument")

        filters = {view.assessment_filter_args: view.assessment.id}
        return queryset.filter(**filters)
