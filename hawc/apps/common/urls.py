from django.conf import settings
from rest_framework.routers import DefaultRouter

from hawc.apps.common.api import healthcheck

healthcheck_url = (
    f"healthcheck/{settings.HEALTHCHECK_URL_PREFIX}"
    if settings.HEALTHCHECK_URL_PREFIX
    else "healthcheck"
)
router = DefaultRouter()

router.register(f"{healthcheck_url}/api", healthcheck.HealthcheckViewset, basename="healthcheck")
