from django.conf import settings
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .api import healthcheck

healthcheck_url = (
    "healthcheck" if settings.DEBUG else f"healthcheck/{settings.HEALTHCHECK_URL_PREFIX}"
)

router = SimpleRouter()
router.register(healthcheck_url, healthcheck.HealthcheckViewSet, basename="healthcheck")

app_name = "common"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
]
