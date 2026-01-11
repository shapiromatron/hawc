from typing import Any

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView
from rest_framework.routers import SimpleRouter

from . import api, views


def get_admin_urlpatterns(open_api_patterns) -> list:
    """Return a list of admin patterns for inclusion. If Admin is not included via a
    django setting; diagnostic endpoints are still included, but nothing else.
    """

    admin_url = f"admin/{settings.ADMIN_URL_PREFIX}" if settings.ADMIN_URL_PREFIX else "admin"

    # always include API for diagnostics
    router = SimpleRouter()
    router.register(r"diagnostic", api.DiagnosticViewSet, basename="diagnostic")
    if settings.INCLUDE_ADMIN:
        router.register(r"dashboard", api.DashboardViewSet, basename="admin_dashboard")
        router.register(r"reports", api.ReportsViewSet, basename="admin_reports")
        open_api_patterns.append(path(f"{admin_url}/api/", include(router.urls)))
        admin.autodiscover()

    # use admin prefix if one exists
    patterns: list[Any] = [
        path(f"{admin_url}/api/", include((router.urls, "api"))),
    ]

    if settings.INCLUDE_ADMIN:
        login_view = RedirectView.as_view(url=reverse_lazy("user:login"))
        # extend URL patterns
        patterns.extend(
            [
                # swagger + openapi
                path(f"{admin_url}/api/swagger/", views.Swagger.as_view(), name="swagger"),
                path(
                    f"{admin_url}/api/openapi/",
                    SpectacularAPIView.as_view(),
                    name="openapi",
                ),
                # dashboard
                path(f"{admin_url}/dashboard/", views.Dashboard.as_view(), name="admin_dashboard"),
                # media preview
                path(
                    f"{admin_url}/media-preview/",
                    views.MediaPreview.as_view(),
                    name="admin_media_preview",
                ),
                # site
                path(f"{admin_url}/login/", login_view),
                path(f"{admin_url}/", admin.site.urls),
            ]
        )
    return patterns
