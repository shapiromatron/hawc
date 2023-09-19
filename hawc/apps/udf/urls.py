from django.conf import settings
from django.urls import path, re_path

from . import views

app_name = "udf"
urlpatterns = (
    [
        path("", views.UDFListView.as_view(), name="udf_list"),
        path("create/", views.CreateUDFView.as_view(), name="udf_create"),
        path("<int:pk>/update/", views.UpdateUDFView.as_view(), name="udf_update"),
        path("<int:pk>/", views.UDFDetailView.as_view(), name="udf_detail"),
        re_path(
            r"^schema-preview/(?P<field>schema)/$",
            views.SchemaPreview.as_view(),
            name="schema_preview",
        ),
    ]
    if settings.HAWC_FEATURES.ENABLE_UDF
    else []
)
