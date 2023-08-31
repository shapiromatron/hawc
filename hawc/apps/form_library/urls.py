from django.urls import path, re_path

from . import views

app_name = "form_library"
urlpatterns = [
    # Create a Data Extraction form
    path(
        "form/create/",
        views.CreateDataExtractionView.as_view(),
        name="form_create",
    ),
    re_path(
        r"^form/schema-preview/(?P<field>schema)/$",
        views.SchemaPreview.as_view(),
        name="schema_preview",
    ),
]
