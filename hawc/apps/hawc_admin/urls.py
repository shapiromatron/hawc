from django.conf import settings
from django.contrib import admin
from django.urls import path

from . import views

admin_url = f"admin/{settings.ADMIN_URL_PREFIX}" if settings.ADMIN_URL_PREFIX else "admin"
urlpatterns = [
    # swagger site
    path(f"{admin_url}/api/swagger/", views.Swagger.as_view(), name="swagger"),
    # dashboard views
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
    # admin media preview
    path(f"{admin_url}/media-preview/", views.MediaPreview.as_view(), name="admin_media_preview"),
    # admin site
    path(f"{admin_url}/", admin.site.urls),
]
admin.autodiscover()
