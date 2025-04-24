from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"ehv", api.EhvTermViewSet, basename="ehv")
router.register(r"toxrefdb", api.ToxRefDBTermViewSet, basename="toxrefdb")
router.register(r"term", api.TermViewSet, basename="term")
router.register(r"guideline_profile", api.GuidelineProfileViewSet, basename="guideline_profile")

app_name = "vocab"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    path("ehv/", views.EhvBrowse.as_view(), name="ehv-browse"),
    path("toxrefdb/", views.ToxRefDBBrowse.as_view(), name="toxrefdb-browse"),
    # Observations
    path(
        "experiment/<int:pk>/observations/",
        views.ObservationList.as_view(),
        name="observation-list",
    ),
    path(
        "observation/<int:pk>/<str:status>/<slug:action>/",
        views.ObservationViewSet.as_view(),
        name="observation-htmx",
    ),
]

admin.autodiscover()
