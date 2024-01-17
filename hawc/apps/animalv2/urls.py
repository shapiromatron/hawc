from django.urls import path

from . import views

app_name = "animalv2"
urlpatterns = [
    # Experiment
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
        "experimentv2/<int:pk>/",
        views.ExperimentViewSet.as_view(),
        {"action": "read"},
        name="experiment-detail",
    ),
    path(
        "experimentv2/<int:pk>/update/",
        views.ExperimentViewSet.as_view(),
        {"action": "update"},
        name="experiment-update",
    ),
]
