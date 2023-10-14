from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"session", api.Session, basename="session")

app_name = "bmd"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    # BMD assessment-level settings
    path(
        "assessment/<int:pk>/settings/",
        views.AssessmentSettingsDetail.as_view(),
        name="assess_settings_detail",
    ),
    path(
        "assessment/<int:pk>/settings/update/",
        views.AssessSettingsUpdate.as_view(),
        name="assess_settings_update",
    ),
    # BMD create/read/update views
    path(
        "endpoint/<int:pk>/create/",
        views.SessionCreate.as_view(),
        name="session_create",
    ),
    path("endpoint/<int:pk>/", views.SessionList.as_view(), name="session_list"),
    path("session/<int:pk>/", views.SessionDetail.as_view(), name="session_detail"),
    path(
        "session/<int:pk>/update/",
        views.SessionUpdate.as_view(),
        name="session_update",
    ),
    path(
        "session/<int:pk>/delete/",
        views.SessionDelete.as_view(),
        name="session_delete",
    ),
]
