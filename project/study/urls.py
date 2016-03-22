from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views, api


router = DefaultRouter()
router.register(r'study', api.Study, base_name="study")
router.register(r'domain', api.StudyQualityDomain, base_name='domain')

urlpatterns = [
    url(r'^api/', include(router.urls)),

    # assessment risk-of-bias
    url(r'^assessment/(?P<pk>\d+)/risk-of-bias/$',
        views.ASQDetail.as_view(),
        name='asq_detail'),
    url(r'^assessment/(?P<pk>\d+)/risk-of-bias/edit/$',
        views.ASQEdit.as_view(),
        name='asq_update'),
    url(r'^assessment/(?P<pk>\d+)/risk-of-bias/copy/$',
        views.ASQCopy.as_view(),
        name='asq_copy'),
    url(r'^assessment/(?P<pk>\d+)/risk-of-bias/report/$',
        views.StudyBiasExport.as_view(),
        name='bias_export'),
    url(r'^assessment/(?P<pk>\d+)/risk-of-bias/fixed-report/$',
        views.SQFixedReport.as_view(),
        name='sq_fixedreport'),

    url(r'^assessment/(?P<pk>\d+)/risk-of-bias-domain/create/$',
        views.SQDomainCreate.as_view(),
        name='sqd_create'),
    url(r'^risk-of-bias-domain/(?P<pk>\d+)/edit/$',
        views.SQDomainUpdate.as_view(),
        name='sqd_update'),
    url(r'^risk-of-bias-domain/(?P<pk>\d+)/delete/$',
        views.SQDomainDelete.as_view(),
        name='sqd_delete'),

    url(r'^risk-of-bias-domain/(?P<pk>\d+)/metric/create/$',
        views.SQMetricCreate.as_view(),
        name='sqm_create'),
    url(r'^risk-of-bias-metric/(?P<pk>\d+)/edit/$',
        views.SQMetricUpdate.as_view(),
        name='sqm_update'),
    url(r'^risk-of-bias-metric/(?P<pk>\d+)/delete/$',
        views.SQMetricDelete.as_view(),
        name='sqm_delete'),

    # study
    url(r'^assessment/(?P<pk>\d+)/$',
        views.StudyList.as_view(),
        name='list'),
    url(r'^(?P<pk>\d+)/add-details/$',
        views.StudyCreateFromReference.as_view(),
        name='new_study'),
    url(r'^assessment/(?P<pk>\d+)/new-study/$',
        views.ReferenceStudyCreate.as_view(),
        name='new_ref'),
    url(r'^assessment/(?P<pk>\d+)/report/',
        views.StudyReport.as_view(),
        name='studies_report'),
    url(r'^assessment/(?P<pk>\d+)/copy-studies/$',
        views.StudiesCopy.as_view(),
        name='studies_copy'),

    url(r'^(?P<pk>\d+)/$',
        views.StudyRead.as_view(),
        name='detail'),
    url(r'^(?P<pk>\d+)/edit/$',
        views.StudyUpdate.as_view(),
        name='update'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.StudyDelete.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/versions/$',
        views.StudyVersions.as_view(),
        name='versions'),

    # attachment
    url(r'^attachment/(?P<pk>\d+)/$',
        views.AttachmentRead.as_view(),
        name='attachment_detail'),
    url(r'^(?P<pk>\d+)/attachment/add/$',
        views.AttachmentCreate.as_view(),
        name='attachment_create'),
    url(r'^attachment/(?P<pk>\d+)/delete/$',
        views.AttachmentDelete.as_view(),
        name='attachment_delete'),

    # risk-of-bias at study-level
    url(r'^(?P<pk>\d+)/risk-of-bias/$',
        views.SQsDetail.as_view(),
        name='sqs_detail'),
    url(r'^(?P<pk>\d+)/risk-of-bias/create/$',
        views.SQsCreate.as_view(),
        name='sqs_new'),
    url(r'^(?P<pk>\d+)/risk-of-bias/edit/$',
        views.SQsEdit.as_view(),
        name='sqs_update'),
    url(r'^(?P<pk>\d+)/risk-of-bias/delete/$',
        views.SQsDelete.as_view(),
        name='sqs_delete'),

    # risk-of-bias
    url(r'^risk-of-bias/(?P<slug>[\w-]+)/(?P<pk>\d+)/create/',
        views.SQCreate.as_view(),
        name='sq_create'),
    url(r'^risk-of-bias/(?P<pk>\d+)/edit/$',
        views.SQEdit.as_view(),
        name='sq_update'),
    url(r'^risk-of-bias/(?P<pk>\d+)/delete/$',
        views.SQDelete.as_view(),
        name='sq_delete'),
]
