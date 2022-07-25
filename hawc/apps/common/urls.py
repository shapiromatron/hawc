from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hawc.apps.common.api import healthcheck

healthcheck_url = (
    "healthcheck" if settings.DEBUG else f"healthcheck/{settings.HEALTHCHECK_URL_PREFIX}"
)

router = DefaultRouter()
router.register(healthcheck_url, healthcheck.HealthcheckViewset, basename="healthcheck")

app_name = "common"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
]
