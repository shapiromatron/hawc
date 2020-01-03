from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views, api


router = DefaultRouter()
router.register(r'endpoint',
                api.Endpoint,
                base_name="endpoint")
router.register(r'experiment',
                api.Experiment,
                base_name="experiment")
router.register(r'animal-group',
                api.AnimalGroup,
                base_name="animal_group")
router.register(r'experiment-cleanup',
                api.ExperimentCleanupFieldsView,
                base_name="experiment-cleanup")
router.register(r'animal_group-cleanup',
                api.AnimalGroupCleanupFieldsView,
                base_name="animal_group-cleanup")
router.register(r'endpoint-cleanup',
                api.EndpointCleanupFieldsView,
                base_name="endpoint-cleanup")
router.register(r'dosingregime-cleanup',
                api.DosingRegimeCleanupFieldsView,
                base_name="dosingregime-cleanup")
router.register(r'dose-units',
                api.DoseUnits,
                base_name="dose_units")


urlpatterns = [
    url(r'^api/', include(router.urls, namespace='api')),

    # Overall views
    url(r'^assessment/(?P<pk>\d+)/full-export/$',
        views.FullExport.as_view(),
        name='export'),
    url(r'^assessment/(?P<pk>\d+)/endpoint-export/$',
        views.EndpointExport.as_view(),
        name='endpoint_export'),

    # Experiment
    url(r'^study/(?P<pk>\d+)/experiment/new/$',
        views.ExperimentCreate.as_view(),
        name='experiment_new'),
    url(r'^study/(?P<pk>\d+)/experiment/copy-as-new-selector/$',
        views.ExperimentCopyAsNewSelector.as_view(),
        name='experiment_copy_selector'),
    url(r'^experiment/(?P<pk>\d+)/$',
        views.ExperimentRead.as_view(),
        name='experiment_detail'),
    url(r'^experiment/(?P<pk>\d+)/edit/$',
        views.ExperimentUpdate.as_view(),
        name='experiment_update'),
    url(r'^experiment/(?P<pk>\d+)/delete/$',
        views.ExperimentDelete.as_view(),
        name='experiment_delete'),

    # AnimalGroup
    url(r'^experiment/(?P<pk>\d+)/animal-group/new/$',
        views.AnimalGroupCreate.as_view(),
        name='animal_group_new'),
    url(r'^experiment/(?P<pk>\d+)/animal-group/copy-as-new-selector/$',
        views.AnimalGroupCopyAsNewSelector.as_view(),
        name='animal_group_copy_selector'),
    url(r'^animal-group/(?P<pk>\d+)/$',
        views.AnimalGroupRead.as_view(),
        name='animal_group_detail'),
    url(r'^animal-group/(?P<pk>\d+)/edit/$',
        views.AnimalGroupUpdate.as_view(),
        name='animal_group_update'),
    url(r'^animal-group/(?P<pk>\d+)/delete/$',
        views.AnimalGroupDelete.as_view(),
        name='animal_group_delete'),
    url(r'^animal-group/(?P<pk>\d+)/endpoint/copy-as-new-selector/$',
        views.EndpointCopyAsNewSelector.as_view(),
        name='endpoint_copy_selector'),

    # Dosing Regime
    url(r'^dosing-regime/(?P<pk>\d+)/edit/$',
        views.DosingRegimeUpdate.as_view(),
        name='dosing_regime_update'),

    # Endpoint
    url(r'^assessment/(?P<pk>\d+)/endpoints/$',
        views.EndpointList.as_view(),
        name='endpoint_list'),
    url(r'^assessment/(?P<pk>\d+)/endpoints/tags/(?P<tag_slug>[-\w]+)/$',
        views.EndpointTags.as_view(),
        name='assessment_endpoint_taglist'),
    url(r'^animal-group/(?P<pk>\d+)/endpoint/new/$',
        views.EndpointCreate.as_view(),
        name='endpoint_new'),
    url(r'^endpoint/(?P<pk>\d+)/$',
        views.EndpointRead.as_view(),
        name='endpoint_detail'),
    url(r'^endpoint/(?P<pk>\d+)/edit/$',
        views.EndpointUpdate.as_view(),
        name='endpoint_update'),
    url(r'^endpoint/(?P<pk>\d+)/delete/$',
        views.EndpointDelete.as_view(),
        name='endpoint_delete'),
]
