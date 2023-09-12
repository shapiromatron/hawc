from django.urls import path

from . import views

app_name = "form_library"
urlpatterns = [
    # Create a user defined form
    path(
        "create/",
        views.CreateUDFView.as_view(),
        name="form_create",
    ),
]
