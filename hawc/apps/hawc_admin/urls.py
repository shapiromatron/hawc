from typing import Any, List

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from hawc import __version__

from . import api, schema, views


def get_admin_urlpatterns(open_api_patterns) -> List:
    """Return a list of admin patterns for inclusion. If Admin is not included via a
    django setting; healthchecks are still included, but nothing else.
    """

    admin_url = f"admin/{settings.ADMIN_URL_PREFIX}" if settings.ADMIN_URL_PREFIX else "admin"

    # always include API for healthchecks
    router = DefaultRouter()
    if settings.INCLUDE_ADMIN:
        router.register(r"dashboard", api.DashboardViewset, basename="admin_dashboard")
        open_api_patterns.append(path(f"{admin_url}/api/", include(router.urls)))
        admin.autodiscover()

    # use admin prefix if one exists
    patterns: List[Any] = [
        path(f"{admin_url}/api/", include((router.urls, "api"))),
    ]

    if settings.INCLUDE_ADMIN:
        # extend URL patterns
        patterns.extend(
            [
                # swagger + openapi
                path(f"{admin_url}/api/swagger/", views.Swagger.as_view(), name="swagger"),
                path(
                    f"{admin_url}/api/openapi/",
                    get_schema_view(
                        title="HAWC",
                        version=__version__,
                        patterns=open_api_patterns,
                        permission_classes=(permissions.IsAdminUser,),
                        generator_class=schema.CompleteSchemaGenerator,
                    ),
                    name="openapi",
                ),
                # dashboard
                path(
                    f"{admin_url}/dashboard/",
                    views.Dashboard.as_view(),
                    {"action": "index"},
                    name="admin_dashboard",
                ),
                path(
                    f"{admin_url}/dashboard/growth/",
                    views.Dashboard.as_view(),
                    {"action": "growth"},
                    name="admin_dashboard_growth",
                ),
                path(
                    f"{admin_url}/dashboard/users/",
                    views.Dashboard.as_view(),
                    {"action": "users"},
                    name="admin_dashboard_users",
                ),
                path(
                    f"{admin_url}/dashboard/assessments/",
                    views.Dashboard.as_view(),
                    {"action": "assessment_growth"},
                    name="admin_dashboard_assessments",
                ),
                path(
                    f"{admin_url}/dashboard/assessment-profile/",
                    views.Dashboard.as_view(),
                    {"action": "assessment_profile"},
                    name="admin_dashboard_assessment_profile",
                ),
                path(
                    f"{admin_url}/dashboard/assessment-size/",
                    views.Dashboard.as_view(),
                    {"action": "assessment_size"},
                    name="admin_dashboard_assessment_size",
                ),
                path(
                    f"{admin_url}/dashboard/daily-changes/",
                    views.Dashboard.as_view(),
                    {"action": "daily_changes"},
                    name="admin_dashboard_changes",
                ),
                # media preview
                path(
                    f"{admin_url}/media-preview/",
                    views.MediaPreview.as_view(),
                    name="admin_media_preview",
                ),
                # site
                path(f"{admin_url}/", admin.site.urls),
            ]
        )
    return patterns
