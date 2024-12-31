from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"assessment", api.AnimalAssessmentViewSet, basename="assessment")
router.register(r"endpoint", api.Endpoint, basename="endpoint")
router.register(r"experiment", api.Experiment, basename="experiment")
router.register(r"animal-group", api.AnimalGroup, basename="animal_group")
router.register(
    r"experiment-cleanup",
    api.ExperimentCleanupFieldsView,
    basename="experiment-cleanup",
)
router.register(
    r"animal_group-cleanup",
    api.AnimalGroupCleanupFieldsView,
    basename="animal_group-cleanup",
)
router.register(r"endpoint-cleanup", api.EndpointCleanupFieldsView, basename="endpoint-cleanup")
router.register(
    r"dosingregime-cleanup",
    api.DosingRegimeCleanupFieldsView,
    basename="dosingregime-cleanup",
)
router.register(r"dose-units", api.DoseUnits, basename="dose_units")
router.register(r"metadata", api.Metadata, basename="metadata")


app_name = "animal"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    # Heatmap views
    path(
        "assessment/<int:pk>/heatmap-study-design/",
        views.HeatmapStudyDesign.as_view(),
        name="heatmap_study_design",
    ),
    path(
        "assessment/<int:pk>/heatmap-endpoints/",
        views.HeatmapEndpoint.as_view(),
        name="heatmap_endpoints",
    ),
    path(
        "assessment/<int:pk>/heatmap-endpoints-doses/",
        views.HeatmapEndpointDose.as_view(),
        name="heatmap_endpoints_doses",
    ),
    # Experiment
    path(
        "study/<int:pk>/experiment/create/",
        views.ExperimentCreate.as_view(),
        name="experiment_new",
    ),
    path(
        "study/<int:pk>/experiment/copy/",
        views.ExperimentCopyForm.as_view(),
        name="experiment_copy",
    ),
    path(
        "experiment/<int:pk>/",
        views.ExperimentDetail.as_view(),
        name="experiment_detail",
    ),
    path(
        "experiment/<int:pk>/update/",
        views.ExperimentUpdate.as_view(),
        name="experiment_update",
    ),
    path(
        "experiment/<int:pk>/delete/",
        views.ExperimentDelete.as_view(),
        name="experiment_delete",
    ),
    path("assessment/<int:pk>/", views.ExperimentFilterList.as_view(), name="experiment_list"),
    # AnimalGroup
    path(
        "experiment/<int:pk>/animal-group/create/",
        views.AnimalGroupCreate.as_view(),
        name="animal_group_new",
    ),
    path(
        "experiment/<int:pk>/animal-group/copy/",
        views.AnimalGroupCopyForm.as_view(),
        name="animal_group_copy",
    ),
    path(
        "animal-group/<int:pk>/",
        views.AnimalGroupDetail.as_view(),
        name="animal_group_detail",
    ),
    path(
        "animal-group/<int:pk>/update/",
        views.AnimalGroupUpdate.as_view(),
        name="animal_group_update",
    ),
    path(
        "animal-group/<int:pk>/delete/",
        views.AnimalGroupDelete.as_view(),
        name="animal_group_delete",
    ),
    path(
        "animal-group/<int:pk>/endpoint/copy/",
        views.EndpointCopyForm.as_view(),
        name="endpoint_copy",
    ),
    # Dosing Regime
    path(
        "dosing-regime/<int:pk>/update/",
        views.DosingRegimeUpdate.as_view(),
        name="dosing_regime_update",
    ),
    # Endpoint
    path(
        "assessment/<int:pk>/endpoints/",
        views.EndpointFilterList.as_view(),
        name="endpoint_list",
    ),
    path(
        "assessment/<int:pk>/endpoints-v2/",
        views.EndpointListV2.as_view(),
        name="endpoint_list_v2",
    ),
    path(
        "animal-group/<int:pk>/endpoint/create/",
        views.EndpointCreate.as_view(),
        name="endpoint_new",
    ),
    path("endpoint/<int:pk>/", views.EndpointDetail.as_view(), name="endpoint_detail"),
    path(
        "endpoint/<int:pk>/update/",
        views.EndpointUpdate.as_view(),
        name="endpoint_update",
    ),
    path(
        "endpoint/<int:pk>/delete/",
        views.EndpointDelete.as_view(),
        name="endpoint_delete",
    ),
]
