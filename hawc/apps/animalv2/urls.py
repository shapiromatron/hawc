from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register("experiment", api.ExperimentViewSet, basename="experiment")
router.register("chemical", api.ChemicalViewSet, basename="chemical")
router.register("animal-group", api.AnimalGroupViewSet, basename="animal-group")
router.register("treatment", api.TreatmentViewSet, basename="treatment")
router.register("dose-group", api.DoseGroupViewSet, basename="dose-group")
router.register("endpoint", api.EndpointViewSet, basename="endpoint")
router.register("observation-time", api.ObservationTimeViewSet, basename="observation-time")
router.register("data-extraction", api.DataExtractionViewSet, basename="data-extraction")
router.register(
    "dose-response-group-level-data",
    api.DoseResponseGroupLevelDataViewSet,
    basename="dose-response-group-level-data",
)
router.register(
    "dose-response-animal-level-data",
    api.DoseResponseAnimalLevelDataViewSet,
    basename="dose-response-animal-level-data",
)
router.register("study-level-value", api.StudyLevelValueViewSet, basename="study-level-value")

app_name = "animalv2"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
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
    path("assessment/<int:pk>/", views.ExperimentFilterList.as_view(), name="experiment_list"),
    path(
        "experiment/<int:pk>/delete/",
        views.ExperimentDelete.as_view(),
        name="experiment_delete",
    ),
    # HTMX ViewSet
    path(
        "experimentv2/<int:pk>/<slug:action>/",
        views.ExperimentViewSet.as_view(),
        name="experiment-htmx",
    ),
    path(
        "chemical/<int:pk>/<slug:action>/",
        views.ChemicalViewSet.as_view(),
        name="chemical-htmx",
    ),
    path(
        "animalgroup/<int:pk>/<slug:action>/",
        views.AnimalGroupViewSet.as_view(),
        name="animalgroup-htmx",
    ),
    path(
        "treatment/<int:pk>/<slug:action>/",
        views.TreatmentViewSet.as_view(),
        name="treatment-htmx",
    ),
    path(
        "endpoint/<int:pk>/<slug:action>/",
        views.EndpointViewSet.as_view(),
        name="endpoint-htmx",
    ),
    path(
        "observationtime/<int:pk>/<slug:action>/",
        views.ObservationTimeViewSet.as_view(),
        name="observationtime-htmx",
    ),
    path(
        "dataextraction/<int:pk>/<slug:action>/",
        views.DataExtractionViewSet.as_view(),
        name="dataextraction-htmx",
    ),
    # Study Level Values
    path(
        "study/<int:pk>/study-level-values/",
        views.StudyLevelValues.as_view(),
        name="studylevelvalues",
    ),
    path(
        "study-level-values/<int:pk>/<slug:action>/",
        views.StudyLevelValueViewSet.as_view(),
        name="studylevelvalues-htmx",
    ),
]
