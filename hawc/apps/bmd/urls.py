from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"session", api.Session, base_name="session")

app_name = "bmd"
urlpatterns = [
    url(r"^api/", include(router.urls, namespace="api")),
    # BMD assessment-level settings
    url(
        r"^assessment/(?P<pk>\d+)/settings/$",
        views.AssessSettingsRead.as_view(),
        name="assess_settings_detail",
    ),
    url(
        r"^assessment/(?P<pk>\d+)/settings/edit/$",
        views.AssessSettingsUpdate.as_view(),
        name="assess_settings_update",
    ),
    url(
        r"^assessment/(?P<pk>\d+)/logic/edit/$",
        views.AssessLogicUpdate.as_view(),
        name="assess_logic_update",
    ),
    # BMD create/read/update views
    url(r"^endpoint/(?P<pk>\d+)/create/$", views.SessionCreate.as_view(), name="session_create",),
    url(r"^endpoint/(?P<pk>\d+)/$", views.SessionList.as_view(), name="session_list"),
    url(r"^session/(?P<pk>\d+)/$", views.SessionDetail.as_view(), name="session_detail"),
    url(r"^session/(?P<pk>\d+)/update/$", views.SessionUpdate.as_view(), name="session_update",),
    url(r"^session/(?P<pk>\d+)/delete/$", views.SessionDelete.as_view(), name="session_delete",),
]
