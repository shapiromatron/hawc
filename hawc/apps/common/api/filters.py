import django_filters as df
from rest_framework import exceptions, filters

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
            raise ValueError("Viewset requires the `assessment_filter_args` argument")

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


class GetFilterBackend(df.rest_framework.DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        return {
            "data": request.query_params,
            "queryset": queryset,
            "request": request,
            "assessment": view.assessment,
        }


class PostFilterBackend(df.rest_framework.DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        return {
            "data": request.data,
            "queryset": queryset,
            "request": request,
            "assessment": view.assessment,
        }
