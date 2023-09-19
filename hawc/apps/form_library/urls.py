from django.conf import settings
from django.urls import path, re_path

from . import views

app_name = "form_library"
urlpatterns = (
    [
        path(
            "all/",
            views.UDFListView.as_view(),
            name="form_list",
        ),
        # UDF CRUD
        path(
            "create/",
            views.CreateUDFView.as_view(),
            name="form_create",
        ),
        path("<int:pk>/update/", views.UpdateUDFView.as_view(), name="form_update"),
        path(
            "<int:pk>/",
            views.UDFDetailView.as_view(),
            name="form_detail",
        ),
        re_path(
            r"^schema-preview/(?P<field>schema)/$",
            views.SchemaPreview.as_view(),
            name="schema_preview",
        ),
    ]
    if settings.HAWC_FEATURES.ENABLE_DYNAMIC_FORMS
    else []
)
