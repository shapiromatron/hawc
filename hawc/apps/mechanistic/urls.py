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
        "study/<int:pk>/experiment/copy/",
        views.ExperimentCopyForm.as_view(),
        name="experiment_copy",
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
    # CHEMICAL - START
    path(
        "study/<int:pk>/chemical/create/",
        views.ChemicalCreate.as_view(),
        name="chemical_create",
    ),
    path(
        "study/<int:pk>/chemical/copy/",
        views.ChemicalCopyForm.as_view(),
        name="chemical_copy",
    ),
    path(
        "chemical/<int:pk>/update/",
        views.ChemicalUpdate.as_view(),
        name="chemical_update",
    ),
    path(
        "chemical/<int:pk>/",
        views.ChemicalDetail.as_view(),
        name="chemical_detail",
    ),
    path(
        "chemical/<int:pk>/delete/",
        views.ChemicalDelete.as_view(),
        name="chemical_delete",
    ),
    # chemical
    # path(
    # "chemical/<int:pk>/<slug:action>/",
    # views.ChemicalViewSet.as_view(),
    # name="chemical-htmx",
    # ),
    # test system
    path(
        "testsystem/<int:pk>/<slug:action>/",
        views.TestSystemViewSet.as_view(),
        name="testsystem-htmx",
    ),
]
