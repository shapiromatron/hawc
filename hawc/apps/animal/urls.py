from django.conf.urls import include, url
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


app_name = "animal"
urlpatterns = [
    url(r"^api/", include((router.urls, "api"))),
    # Heatmap views
    url(
        r"^assessment/(?P<pk>\d+)/heatmap-study-design/$",
        views.HeatmapStudyDesign.as_view(),
        name="heatmap_study_design",
    ),
    url(
        r"^assessment/(?P<pk>\d+)/heatmap-endpoints/$",
        views.HeatmapEndpoint.as_view(),
        name="heatmap_endpoints",
    ),
    # Experiment
    url(
        r"^study/(?P<pk>\d+)/experiment/new/$",
        views.ExperimentCreate.as_view(),
        name="experiment_new",
    ),
    url(
        r"^study/(?P<pk>\d+)/experiment/copy-as-new-selector/$",
        views.ExperimentCopyAsNewSelector.as_view(),
        name="experiment_copy_selector",
    ),
    url(r"^experiment/(?P<pk>\d+)/$", views.ExperimentRead.as_view(), name="experiment_detail",),
    url(
        r"^experiment/(?P<pk>\d+)/edit/$",
        views.ExperimentUpdate.as_view(),
        name="experiment_update",
    ),
    url(
        r"^experiment/(?P<pk>\d+)/delete/$",
        views.ExperimentDelete.as_view(),
        name="experiment_delete",
    ),
    # AnimalGroup
    url(
        r"^experiment/(?P<pk>\d+)/animal-group/new/$",
        views.AnimalGroupCreate.as_view(),
        name="animal_group_new",
    ),
    url(
        r"^experiment/(?P<pk>\d+)/animal-group/copy-as-new-selector/$",
        views.AnimalGroupCopyAsNewSelector.as_view(),
        name="animal_group_copy_selector",
    ),
    url(
        r"^animal-group/(?P<pk>\d+)/$", views.AnimalGroupRead.as_view(), name="animal_group_detail",
    ),
    url(
        r"^animal-group/(?P<pk>\d+)/edit/$",
        views.AnimalGroupUpdate.as_view(),
        name="animal_group_update",
    ),
    url(
        r"^animal-group/(?P<pk>\d+)/delete/$",
        views.AnimalGroupDelete.as_view(),
        name="animal_group_delete",
    ),
    url(
        r"^animal-group/(?P<pk>\d+)/endpoint/copy-as-new-selector/$",
        views.EndpointCopyAsNewSelector.as_view(),
        name="endpoint_copy_selector",
    ),
    # Dosing Regime
    url(
        r"^dosing-regime/(?P<pk>\d+)/edit/$",
        views.DosingRegimeUpdate.as_view(),
        name="dosing_regime_update",
    ),
    # Endpoint
    url(
        r"^assessment/(?P<pk>\d+)/endpoints/$", views.EndpointList.as_view(), name="endpoint_list",
    ),
    url(
        r"^assessment/(?P<pk>\d+)/endpoints/tags/(?P<tag_slug>[-\w]+)/$",
        views.EndpointTags.as_view(),
        name="assessment_endpoint_taglist",
    ),
    url(
        r"^animal-group/(?P<pk>\d+)/endpoint/new/$",
        views.EndpointCreate.as_view(),
        name="endpoint_new",
    ),
    url(r"^endpoint/(?P<pk>\d+)/$", views.EndpointRead.as_view(), name="endpoint_detail"),
    url(r"^endpoint/(?P<pk>\d+)/edit/$", views.EndpointUpdate.as_view(), name="endpoint_update",),
    url(r"^endpoint/(?P<pk>\d+)/delete/$", views.EndpointDelete.as_view(), name="endpoint_delete",),
]
