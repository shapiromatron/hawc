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
    # chemical
    path(
        "chemical/<int:pk>/create/",
        views.ChemicalViewSet.as_view(),
        {"action": "create"},
        name="chemical-create",
    ),
    path(
        "chemical/<int:pk>/",
        views.ChemicalViewSet.as_view(),
        {"action": "read"},
        name="chemical-detail",
    ),
    path(
        "chemical/<int:pk>/clone/",
        views.ChemicalViewSet.as_view(),
        {"action": "clone"},
        name="chemical-clone",
    ),
    path(
        "chemical/<int:pk>/update/",
        views.ChemicalViewSet.as_view(),
        {"action": "update"},
        name="chemical-update",
    ),
    path(
        "chemical/<int:pk>/delete/",
        views.ChemicalViewSet.as_view(),
        {"action": "delete"},
        name="chemical-delete",
    ),
    # animalgroup
    path(
        "animalgroup/<int:pk>/create/",
        views.AnimalGroupViewSet.as_view(),
        {"action": "create"},
        name="animalgroup-create",
    ),
    path(
        "animalgroup/<int:pk>/",
        views.AnimalGroupViewSet.as_view(),
        {"action": "read"},
        name="animalgroup-detail",
    ),
    path(
        "animalgroup/<int:pk>/clone/",
        views.AnimalGroupViewSet.as_view(),
        {"action": "clone"},
        name="animalgroup-clone",
    ),
    path(
        "animalgroup/<int:pk>/update/",
        views.AnimalGroupViewSet.as_view(),
        {"action": "update"},
        name="animalgroup-update",
    ),
    path(
        "animalgroup/<int:pk>/delete/",
        views.AnimalGroupViewSet.as_view(),
        {"action": "delete"},
        name="animalgroup-delete",
    ),
    # treatment
    path(
        "treatment/<int:pk>/create/",
        views.TreatmentViewSet.as_view(),
        {"action": "create"},
        name="treatment-create",
    ),
    path(
        "treatment/<int:pk>/",
        views.TreatmentViewSet.as_view(),
        {"action": "read"},
        name="treatment-detail",
    ),
    path(
        "treatment/<int:pk>/clone/",
        views.TreatmentViewSet.as_view(),
        {"action": "clone"},
        name="treatment-clone",
    ),
    path(
        "treatment/<int:pk>/update/",
        views.TreatmentViewSet.as_view(),
        {"action": "update"},
        name="treatment-update",
    ),
    path(
        "treatment/<int:pk>/delete/",
        views.TreatmentViewSet.as_view(),
        {"action": "delete"},
        name="treatment-delete",
    ),
]
