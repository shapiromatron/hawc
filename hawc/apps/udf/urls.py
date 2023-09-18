from django.conf import settings
from django.urls import path

from . import views

app_name = "udf"
urlpatterns = (
    [
        path("create/", views.CreateUDFView.as_view(), name="udf_create"),
    ]
    if settings.HAWC_FEATURES.ENABLE_UDF
    else []
)
