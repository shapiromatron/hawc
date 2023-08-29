from django.urls import path

from . import views

app_name = "form_library"
urlpatterns = [
    # Create a Data Extraction form
    path(
        "form/create/",
        views.CreateDataExtractionView.as_view(),
        name="form_create",
    ),
]
