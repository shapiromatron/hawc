from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"session", api.Session, basename="session")

app_name = "bmd"
urlpatterns = [
    re_path(r"^api/", include((router.urls, "api"))),
    # BMD assessment-level settings
    re_path(
        r"^assessment/(?P<pk>\d+)/settings/$",
        views.AssessSettingsRead.as_view(),
        name="assess_settings_detail",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/settings/edit/$",
        views.AssessSettingsUpdate.as_view(),
        name="assess_settings_update",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/logic/edit/$",
        views.AssessLogicUpdate.as_view(),
        name="assess_logic_update",
    ),
    # BMD create/read/update views
    re_path(
        r"^endpoint/(?P<pk>\d+)/create/$", views.SessionCreate.as_view(), name="session_create",
    ),
    re_path(r"^endpoint/(?P<pk>\d+)/$", views.SessionList.as_view(), name="session_list"),
    re_path(r"^session/(?P<pk>\d+)/$", views.SessionDetail.as_view(), name="session_detail"),
    re_path(
        r"^session/(?P<pk>\d+)/update/$", views.SessionUpdate.as_view(), name="session_update",
    ),
    re_path(
        r"^session/(?P<pk>\d+)/delete/$", views.SessionDelete.as_view(), name="session_delete",
    ),
]
