from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import (HAWCUserList, HAWCUserDetail,
                       AssessmentList, AssessmentDetail,
                       StudyList, StudyDetail,
                       ExperimentList, ExperimentDetail,
                       AnimalGroupList, AnimalGroupDetail,
                       EndpointList, EndpointDetail,
                       AggregationList, AggregationDetail)

urlpatterns = patterns('api.views',

    # base URL launch-view
    url(r'^$', 'api_root', name='api_root'),

    # user information
    url(r'^users/$', HAWCUserList.as_view(), name='hawcuser-list'),
    url(r'^users/(?P<pk>\d+)/$', HAWCUserDetail.as_view(), name='hawcuser-detail'),

    # list views
    url(r'^assessment/$', AssessmentList.as_view(), name='assessment-list'),
    url(r'^assessment/(?P<pk>\d+)/study/$', StudyList.as_view(), name='study-list'),
    url(r'^assessment/(?P<pk>\d+)/experiment/$', ExperimentList.as_view(), name='experiment-list'),
    url(r'^assessment/(?P<pk>\d+)/animal-group/$', AnimalGroupList.as_view(), name='animal-group-list'),
    url(r'^assessment/(?P<pk>\d+)/endpoint/$', EndpointList.as_view(), name='endpoint-list'),
    url(r'^assessment/(?P<pk>\d+)/aggregation/$', AggregationList.as_view(), name='aggregation-list'),

    # detail views
    url(r'^assessment/(?P<pk>\d+)/$', AssessmentDetail.as_view(), name='assessment-detail'),
    url(r'^study/(?P<pk>\d+)/$', StudyDetail.as_view(), name='study-detail'),
    url(r'^experiment/(?P<pk>\d+)/$', ExperimentDetail.as_view(), name='experiment-detail'),
    url(r'^animal-group/(?P<pk>\d+)/$', AnimalGroupDetail.as_view(), name='animalgroup-detail'),
    url(r'^endpoint/(?P<pk>\d+)/$', EndpointDetail.as_view(), name='endpoint-detail'),
    url(r'^aggregation/(?P<pk>\d+)/$', AggregationDetail.as_view(), name='aggregation-detail'),
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])

# Default login/logout views
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
