from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views, api

router = DefaultRouter()
router.register(r'domain', api.RiskOfBiasDomain, base_name='domain')
router.register(r'review', api.RiskOfBias, base_name='review')
router.register(r'metrics', api.AssessmentMetricViewset, base_name='metrics')
router.register(r'answers', api.AssessmentMetricAnswersViewSet, base_name='answers')
router.register(r'metrics/scores', api.AssessmentMetricScoreViewset, base_name='metric_scores')
router.register(r'scores', api.AssessmentScoreViewset, base_name='scores')

urlpatterns = [
    url(r'^api/', include(router.urls, namespace='api')),

    # modify assessment Study Evaluation settings
    url(r'^assessment/(?P<pk>\d+)/$',
        views.ARoBDetail.as_view(),
        name='arob_detail'),
    url(r'^assessment/(?P<pk>\d+)/copy/$',
        views.ARoBCopy.as_view(),
        name='arob_copy'),
    url(r'^assessment/(?P<pk>\d+)/edit/$',
        views.ARoBEdit.as_view(),
        name='arob_update'),

    # reporting
    url(r'^assessment/(?P<pk>\d+)/export/$',
        views.StudyRoBExport.as_view(),
        name='export'),
    url(r'^assessment/(?P<pk>\d+)/complete-export/$',
        views.StudyRoBCompleteExport.as_view(),
        name='complete_export'),

    # modify domains
    url(r'^assessment/(?P<pk>\d+)/domain/create/$',
        views.RoBDomainCreate.as_view(),
        name='robd_create'),
    url(r'^domain/(?P<pk>\d+)/edit/$',
        views.RoBDomainUpdate.as_view(),
        name='robd_update'),
    url(r'^domain/(?P<pk>\d+)/delete/$',
        views.RoBDomainDelete.as_view(),
        name='robd_delete'),

    # modify metrics
    url(r'^domain/(?P<pk>\d+)/metric/create/$',
        views.RoBMetricCreate.as_view(),
        name='robm_create'),
    url(r'^metric/(?P<pk>\d+)/edit/$',
        views.RoBMetricUpdate.as_view(),
        name='robm_update'),
    url(r'^metric/(?P<pk>\d+)/delete/$',
        views.RoBMetricDelete.as_view(),
        name='robm_delete'),

    # modify metric answers
    url(r'^metric/(?P<pk>\d+)/answers/create/$',
        views.RoBMetricAnswersCreate.as_view(),
        name='robm_answers_create'),
    url(r'^answers/(?P<pk>\d+)/edit/$',
        views.RoBMetricAnswersUpdate.as_view(),
        name='robm_answers_update'),
    url(r'answers/(?P<pk>\d+)/delete/$',
        views.RoBMetricAnswersDelete.as_view(),
        name='robm_answers_delete'),

    # Study Evaluation reviewers
    url(r'^assessment/(?P<pk>\d+)/study-assignments/$',
        views.ARoBReviewersList.as_view(),
        name='arob_reviewers'),
    url(r'^assessment/(?P<pk>\d+)/study-assignments/edit/$',
        views.ARoBReviewersUpdate.as_view(),
        name='arob_reviewers_update'),

    # Study Evaluation at study-level
    url(r'^study/(?P<pk>\d+)/$',
        views.RoBDetail.as_view(),
        name='rob_detail'),
    url(r'^study/(?P<pk>\d+)/all/$',
        views.RoBsDetailAll.as_view(),
        name='rob_detail_all'),

    # Study Evaluation editing views
    url(r'^(?P<pk>\d+)/edit/$',
        views.RoBEdit.as_view(),
        name='rob_update'),

]
