from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views, api

router = DefaultRouter()
router.register(r'domain', api.RiskOfBiasDomain, base_name='domain')

urlpatterns = [
    url(r'^api/', include(router.urls, namespace='api')),

    # assessment risk-of-bias
    url(r'^assessment/(?P<pk>\d+)/$',
        views.ARoBDetail.as_view(),
        name='arob_detail'),
    url(r'^assessment/(?P<pk>\d+)/edit/$',
        views.ARoBEdit.as_view(),
        name='arob_update'),
    url(r'^assessment/(?P<pk>\d+)/copy/$',
        views.ARoBCopy.as_view(),
        name='arob_copy'),
    url(r'^assessment/(?P<pk>\d+)/report/$',
        views.StudyRoBExport.as_view(),
        name='bias_export'),
    url(r'^assessment/(?P<pk>\d+)/fixed-report/$',
        views.RoBFixedReport.as_view(),
        name='rob_fixedreport'),
    url(r'^assessment/(?P<pk>\d+)/studies/$',
        views.ARobList.as_view(),
        name='list'),

    url(r'^assessment/(?P<pk>\d+)/reviewers/$',
        views.ARoBReviewersList.as_view(),
        name='arob_reviewers'),
    url(r'^assessment/(?P<pk>\d+)/reviewers/create/$',
        views.ARoBReviewersCreate.as_view(),
        name='arob_reviewers_create'),
    url(r'^assessment/(?P<pk>\d+)/reviewers/edit/$',
        views.ARoBReviewersUpdate.as_view(),
        name='arob_reviewers_update'),

    url(r'^assessment/(?P<pk>\d+)/domain/create/$',
        views.RoBDomainCreate.as_view(),
        name='robd_create'),
    url(r'^domain/(?P<pk>\d+)/edit/$',
        views.RoBDomainUpdate.as_view(),
        name='robd_update'),
    url(r'^domain/(?P<pk>\d+)/delete/$',
        views.RoBDomainDelete.as_view(),
        name='robd_delete'),

    url(r'^domain/(?P<pk>\d+)/metric/create/$',
        views.RoBMetricCreate.as_view(),
        name='robm_create'),
    url(r'^metric/(?P<pk>\d+)/edit/$',
        views.RoBMetricUpdate.as_view(),
        name='robm_update'),
    url(r'^metric/(?P<pk>\d+)/delete/$',
        views.RoBMetricDelete.as_view(),
        name='robm_delete'),

    # risk-of-bias at study-level
    url(r'^study/(?P<pk>\d+)/$',
        views.RoBsDetail.as_view(),
        name='robs_detail'),
    url(r'^study/(?P<pk>\d+)/all/$',
        views.RoBsDetailAll.as_view(),
        name='robs_detail_all'),
    url(r'^study/(?P<pk>\d+)/list/$',
        views.RoBsList.as_view(),
        name='robs_list'),

    url(r'^(?P<pk>\d+)/$',
        views.RoBDetail.as_view(),
        name='rob_detail'),
    url(r'^(?P<pk>\d+)/edit/$',
        views.RoBEdit.as_view(),
        name='rob_update'),
    url(r'^(?P<pk>\d+)/edit-final/$',
        views.RoBEditFinal.as_view(),
        name='rob_update_final'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.RoBDelete.as_view(),
        name='rob_delete'),
]
