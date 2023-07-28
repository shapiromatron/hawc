import django_filters as df
from django.db.models import Q
from rest_framework import filters

from ..models import Assessment
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


class GlobalChemicalsFilterSet(df.FilterSet):
    query = df.CharFilter(
        method="filter_query",
        label="Query",
        help_text="Enter chemical name, DTXSID, or CASRN",
    )
    published_only = df.BooleanFilter(method="filter_published_only")  # published_only=true

    def filter_query(self, queryset, name, value):
        query = (
            Q(name__icontains=value)
            | Q(cas=value)
            | Q(dtxsids__dtxsid=value)
            | Q(dtxsids__content__preferredName__icontains=value)
            | Q(dtxsids__content__casrn=value)
        )
        return queryset.filter(query).distinct()

    def filter_published_only(self, queryset, name, value):
        if value is True:
            return queryset.filter(public_on__isnull=False, hide_from_public_page=False)
        return queryset

    class Meta:
        model = Assessment
        fields = ["query", "published_only"]
