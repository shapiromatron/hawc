from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.AnimalAssessmentViewset, basename="assessment")
router.register(r"endpoint", api.Endpoint, basename="endpoint")
router.register(r"experiment", api.Experiment, basename="experiment")
router.register(r"animal-group", api.AnimalGroup, basename="animal_group")
router.register(
    r"experiment-cleanup", api.ExperimentCleanupFieldsView, basename="experiment-cleanup",
)
router.register(
    r"animal_group-cleanup", api.AnimalGroupCleanupFieldsView, basename="animal_group-cleanup",
)
router.register(r"endpoint-cleanup", api.EndpointCleanupFieldsView, basename="endpoint-cleanup")
router.register(
    r"dosingregime-cleanup", api.DosingRegimeCleanupFieldsView, basename="dosingregime-cleanup",
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
        "study/<int:pk>/experiment/new/", views.ExperimentCreate.as_view(), name="experiment_new",
    ),
    path(
        "study/<int:pk>/experiment/copy-as-new-selector/",
        views.ExperimentCopyAsNewSelector.as_view(),
        name="experiment_copy_selector",
    ),
    path("experiment/<int:pk>/", views.ExperimentRead.as_view(), name="experiment_detail",),
    path("experiment/<int:pk>/edit/", views.ExperimentUpdate.as_view(), name="experiment_update",),
    path(
        "experiment/<int:pk>/delete/", views.ExperimentDelete.as_view(), name="experiment_delete",
    ),
    # AnimalGroup
    path(
        "experiment/<int:pk>/animal-group/new/",
        views.AnimalGroupCreate.as_view(),
        name="animal_group_new",
    ),
    path(
        "experiment/<int:pk>/animal-group/copy-as-new-selector/",
        views.AnimalGroupCopyAsNewSelector.as_view(),
        name="animal_group_copy_selector",
    ),
    path("animal-group/<int:pk>/", views.AnimalGroupRead.as_view(), name="animal_group_detail",),
    path(
        "animal-group/<int:pk>/edit/",
        views.AnimalGroupUpdate.as_view(),
        name="animal_group_update",
    ),
    path(
        "animal-group/<int:pk>/delete/",
        views.AnimalGroupDelete.as_view(),
        name="animal_group_delete",
    ),
    path(
        "animal-group/<int:pk>/endpoint/copy-as-new-selector/",
        views.EndpointCopyAsNewSelector.as_view(),
        name="endpoint_copy_selector",
    ),
    # Dosing Regime
    path(
        "dosing-regime/<int:pk>/edit/",
        views.DosingRegimeUpdate.as_view(),
        name="dosing_regime_update",
    ),
    # Endpoint
    path("assessment/<int:pk>/endpoints/", views.EndpointList.as_view(), name="endpoint_list",),
    path(
        "assessment/<int:pk>/endpoints-v2/",
        views.EndpointListV2.as_view(),
        name="endpoint_list_v2",
    ),
    path(
        "assessment/<int:pk>/endpoints/tags/<slug:tag_slug>/",
        views.EndpointTags.as_view(),
        name="assessment_endpoint_taglist",
    ),
    path(
        "animal-group/<int:pk>/endpoint/new/", views.EndpointCreate.as_view(), name="endpoint_new",
    ),
    path("endpoint/<int:pk>/", views.EndpointRead.as_view(), name="endpoint_detail"),
    path("endpoint/<int:pk>/edit/", views.EndpointUpdate.as_view(), name="endpoint_update",),
    path("endpoint/<int:pk>/delete/", views.EndpointDelete.as_view(), name="endpoint_delete",),
]
