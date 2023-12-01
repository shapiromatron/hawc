from django.db.models import QuerySet
from django_filters.filterset import FilterSet
from django_filters.utils import translate_validation
from rest_framework import exceptions, filters
from rest_framework.request import Request

from ..helper import try_parse_list_ints


class CleanupBulkIdFilter(filters.BaseFilterBackend):
    """
    Filters objects in Assessment on GET using InAssessmentFilter.
    Filters objects on ID on PATCH. If ID is not supplied in query_params,
    returns an empty queryset, as entire queryset is updated using Bulk Update.

    IDs must be supplied in the form ?ids=10209,10210.

    """

    def filter_queryset(self, request, queryset, view):
        if not view.assessment_filter_args:
            raise ValueError("ViewSet requires the `assessment_filter_args` argument")

        # always filter queryset by `assessment_id`
        queryset = queryset.filter(**{view.assessment_filter_args: view.assessment.id})

        # required header for bulk-update
        if request._request.method.lower() == "patch":
            ids = list(set(try_parse_list_ints(request.query_params.get("ids"))))
            queryset = queryset.filter(id__in=ids)

            # invalid IDs
            if queryset.count() != len(ids):
                raise exceptions.PermissionDenied()

        return queryset


def filtered_qs(
    queryset: QuerySet, filterset_cls: type[FilterSet], request: Request, **kw
) -> QuerySet:
    """
    Filter a queryset based on a FilterSet and a DRF request.

    This is a utility method to add filtering to custom ViewSet actions, it is adapted from the
    `django_filters.rest_framework.FilterSet` used for standard ViewSet operations.

    Args:
        queryset (QuerySet): the queryset to filter
        filterset_cls (type[filters.FilterSet]): a FilterSet class
        request (Request): a rest framework request
        **kw: any additional arguments provided to FilterSet class constructor
    """
    filterset = filterset_cls(data=request.query_params, queryset=queryset, request=request, **kw)
    if not filterset.is_valid():
        raise translate_validation(filterset.errors)
    return filterset.qs
