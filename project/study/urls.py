from django.conf.urls import patterns, url, include

from rest_framework.routers import DefaultRouter

from . import views, api


router = DefaultRouter()
router.register(r'study', api.Study, base_name="study")

urlpatterns = patterns('',
    #assessment study-quality
    url(r'^assessment/(?P<pk>\d+)/study-quality/$', views.ASQDetail.as_view(), name='asq_detail'),
    url(r'^assessment/(?P<pk>\d+)/study-quality/edit/$', views.ASQEdit.as_view(), name='asq_update'),
    url(r'^assessment/(?P<pk>\d+)/study-quality/report/$', views.StudyBiasExport.as_view(), name='bias_export'),

    url(r'^assessment/(?P<pk>\d+)/study-quality-domain/create/$', views.SQDomainCreate.as_view(), name='sqd_create'),
    url(r'^study-quality-domain/(?P<pk>\d+)/edit/$', views.SQDomainUpdate.as_view(), name='sqd_update'),
    url(r'^study-quality-domain/(?P<pk>\d+)/delete/$', views.SQDomainDelete.as_view(), name='sqd_delete'),

    url(r'^study-quality-domain/(?P<pk>\d+)/metric/create/$', views.SQMetricCreate.as_view(), name='sqm_create'),
    url(r'^study-quality-metric/(?P<pk>\d+)/edit/$', views.SQMetricUpdate.as_view(), name='sqm_update'),
    url(r'^study-quality-metric/(?P<pk>\d+)/delete/$', views.SQMetricDelete.as_view(), name='sqm_delete'),

    #study
    url(r'^assessment/(?P<pk>\d+)/$', views.StudyList.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/add-details/$', views.StudyCreateFromReference.as_view(), name='new_study'),
    url(r'^assessment/(?P<pk>\d+)/new-study/$', views.ReferenceStudyCreate.as_view(), name='new_ref'),
    url(r'^assessment/(?P<pk>\d+)/search/$', views.StudySearch.as_view(), name='search'),
    url(r'^assessment/(?P<pk>\d+)/report/', views.StudyReport.as_view(), name='studies_report'),

    url(r'^(?P<pk>\d+)/$', views.StudyRead.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/json/', views.StudyReadJSON.as_view(), name='json'),
    url(r'^(?P<pk>\d+)/edit/$', views.StudyUpdate.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete/$', views.StudyDelete.as_view(), name='delete'),
    url(r'^(?P<pk>\d+)/versions/$', views.StudyVersions.as_view(), name='versions'),

    # attachment
    url(r'^attachment/(?P<pk>\d+)/$', views.AttachmentRead.as_view(), name='attachment_detail'),
    url(r'^(?P<pk>\d+)/attachment/add/$', views.AttachmentCreate.as_view(), name='attachment_create'),
    url(r'^attachment/(?P<pk>\d+)/delete/$', views.AttachmentDelete.as_view(), name='attachment_delete'),

    #study-quality
    url(r'^(?P<pk>\d+)/study-quality/$', views.SQDetail.as_view(), name='sq_detail'),
    url(r'^(?P<pk>\d+)/study-quality/create/$', views.SQCreate.as_view(), name='sq_new'),
    url(r'^(?P<pk>\d+)/study-quality/edit/$', views.SQEdit.as_view(), name='sq_update'),
    url(r'^(?P<pk>\d+)/study-quality/delete/$', views.SQDelete.as_view(), name='sq_delete'),

    #aggregated study-quality
    url(r'^assessment/(?P<pk>\d+)/study-qualities/heatmap/$', views.SQAggHeatmap.as_view(), name='sq_agg_heatmap'),
    url(r'^assessment/(?P<pk>\d+)/study-qualities/stacked/$', views.SQAggStacked.as_view(), name='sq_agg_stacked_bars'),

    url(r'^api/', include(router.urls))
)
