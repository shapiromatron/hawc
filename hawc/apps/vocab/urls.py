from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from . import api

router = DefaultRouter()
router.register(r"ehv", api.EhvTermViewset, basename="ehv")

app_name = "vocab"
urlpatterns = [
    url(r"^api/", include((router.urls, "api"))),
]

admin.autodiscover()
