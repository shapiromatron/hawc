from django.conf.urls import patterns, url, include

from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r'chemical', api.IVChemical, base_name="chemical")
router.register(r'experiment', api.IVExperiment, base_name="experiment")
router.register(r'endpoint', api.IVEndpoint, base_name="endpoint")

urlpatterns = patterns('',

    # experiment
    url(r'^experiment/(?P<pk>\d+)/$',
        views.ExperimentDetail.as_view(),
        name='experiment_detail'),

    # endpoint
    url(r'^endpoint/(?P<pk>\d+)/$',
        views.EndpointDetail.as_view(),
        name='endpoint_detail'),

    url(r'^assessment/(?P<pk>\d+)/full-export/$',
        views.EndpointsFullExport.as_view(),
        name='endpoints_export'),

    url(r'^assessment/(?P<pk>\d+)/report/$',
        views.EndpointsReport.as_view(),
        name='endpoints_report'),

    url(r'^api/', include(router.urls)),
)
