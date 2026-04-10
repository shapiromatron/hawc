from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

app_name = "mechanistic"
urlpatterns = [
    # CRUD
    path(
        "study/<int:pk>/experiment/create/",
        views.ExperimentCreate.as_view(),
        name="experiment_create",
    ),
    path(
        "experiment/<int:pk>/update/",
        views.ExperimentUpdate.as_view(),
        name="experiment_update",
    ),
    path(
        "experiment/<int:pk>/",
        views.ExperimentDetail.as_view(),
        name="experiment_detail",
    ),
    path(
        "experiment/<int:pk>/delete/",
        views.ExperimentDelete.as_view(),
        name="experiment_delete",
    ),
    # experiment htmx viewset
    path(
        "experimentv2/<int:pk>/<slug:action>/",
        views.ExperimentViewSet.as_view(),
        name="experiment-htmx",
    ),
]

