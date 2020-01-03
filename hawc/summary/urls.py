from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views, api


router = DefaultRouter()
router.register(r'visual', api.Visual, base_name="visual")
router.register(r'data_pivot', api.DataPivot, base_name="data_pivot")


urlpatterns = [

    # API
    url(r'^api/', include(router.urls, namespace='api')),

    # SUMMARY-TEXT
    url(r'^assessment/(?P<pk>\d+)/summaries/$',
        views.SummaryTextList.as_view(),
        name='list'),
    url(r'^assessment/(?P<pk>\d+)/summaries/modify/$',
        views.SummaryTextCreate.as_view(),
        name='create'),
    url(r'^(?P<pk>\d+)/update/$',
        views.SummaryTextUpdate.as_view(),
        name='update'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.SummaryTextDelete.as_view(),
        name='delete'),
    url(r'^assessment/(?P<pk>\d+)/summaries/json/$',
        views.SummaryTextJSON.as_view(),
        name='json'),

    # VISUALIZATIONS
    url(r'^assessment/(?P<pk>\d+)/visuals/$',
        views.VisualizationList.as_view(),
        name='visualization_list'),
    url(r'^assessment/(?P<pk>\d+)/visuals/create/$',
        views.VisualizationCreateSelector.as_view(),
        name='visualization_create_selector'),
    url(r'^assessment/(?P<pk>\d+)/visuals/(?P<visual_type>\d+)/create/$',
        views.VisualizationCreate.as_view(),
        name='visualization_create'),
    url(r'^assessment/(?P<pk>\d+)/type/(?P<visual_type>\d+)/data/$',
        views.VisualizationCreateTester.as_view(),
        name='visualization_create_tester'),
    url(r'^visual/(?P<pk>\d+)/$',
        views.VisualizationDetail.as_view(),
        name='visualization_detail'),
    url(r'^visual/(?P<pk>\d+)/update/$',
        views.VisualizationUpdate.as_view(),
        name='visualization_update'),
    url(r'^visual/(?P<pk>\d+)/delete/$',
        views.VisualizationDelete.as_view(),
        name='visualization_delete'),

    # DATA-PIVOT
    url(r'^data-pivot/assessment/(?P<pk>\d+)/new/$',
        views.DataPivotNewPrompt.as_view(),
        name='dp_new-prompt'),
    url(r'^data-pivot/assessment/(?P<pk>\d+)/new/query/$',
        views.DataPivotQueryNew.as_view(),
        name='dp_new-query'),
    url(r'^data-pivot/assessment/(?P<pk>\d+)/new/file/$',
        views.DataPivotFileNew.as_view(),
        name='dp_new-file'),
    url(r'^data-pivot/assessment/(?P<pk>\d+)/new/copy-as-new-selector/$',
        views.DataPivotCopyAsNewSelector.as_view(),
        name='dp_copy_selector'),

    url(r'^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/$',
        views.DataPivotDetail.as_view(),
        name='dp_detail'),
    url(r'^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/data/$',
        views.DataPivotData.as_view(),
        name='dp_data'),

    url(r'^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/update/$',
        views.DataPivotUpdateSettings.as_view(),
        name='dp_update'),
    url(r'^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/query-update/$',
        views.DataPivotUpdateQuery.as_view(),
        name='dp_query-update'),
    url(r'^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/file-update/$',
        views.DataPivotUpdateFile.as_view(),
        name='dp_file-update'),

    url(r'^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/delete/$',
        views.DataPivotDelete.as_view(),
        name='dp_delete'),
]
