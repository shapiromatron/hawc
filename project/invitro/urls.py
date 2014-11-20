from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',

    # # experiment
    # url(r'^experiment/(?P<pk>\d+)/$',
    #     views.ExperimentDetail.as_view(),
    #     name='experiment_detail'),

    # # endpoint
    # url(r'^endpoint/(?P<pk>\d+)/$',
    #     views.EndpointDetail.as_view(),
    #     name='endpoint_detail'),

    url(r'^assessment/(?P<pk>\d+)/endpoint-flat/$',
        views.EndpointsFlat.as_view(),
        name='endpoints_flat'),

    url(r'^assessment/(?P<pk>\d+)/report/$',
        views.EndpointsReport.as_view(),
        name='endpoints_report'),
)
