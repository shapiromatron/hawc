from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"ehv", api.EhvTermViewSet, basename="ehv")
router.register(r"toxref", api.ToxrefTermViewSet, basename="toxref")
router.register(r"term", api.TermViewSet, basename="term")

app_name = "vocab"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    path("ehv/", views.EhvBrowse.as_view(), name="ehv-browse"),
    path("toxref/", views.ToxrefBrowse.as_view(), name="toxref-browse"),
]

admin.autodiscover()
