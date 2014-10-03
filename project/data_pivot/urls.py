from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.GeneralDataPivot.as_view(), name='general'),

    url(r'^assessment/(?P<pk>\d+)/$',
        views.DataPivotList.as_view(), name='list'),

    url(r'^assessment/(?P<pk>\d+)/new/$',
        views.DataPivotNewPrompt.as_view(), name='new-prompt'),
    url(r'^assessment/(?P<pk>\d+)/new/query/$',
        views.DataPivotQueryNew.as_view(), name='new-query'),
    url(r'^assessment/(?P<pk>\d+)/new/file/$',
        views.DataPivotFileNew.as_view(), name='new-file'),
    url(r'^assessment/(?P<pk>\d+)/new/copy-as-new-selector/$',
        views.DataPivotCopyAsNewSelector.as_view(),
        name='copy_selector'),

    url(r'^assessment/(?P<assessment>\d+)/search/json/$',
        views.DataPivotSearch.as_view(), name='search'),

    url(r'^assessment/(?P<assessment>\d+)/(?P<slug>[\w-]+)/$',
        views.DataPivotDetail.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/json/$',
        views.DataPivotJSON.as_view(), name='json'),

    url(r'^assessment/(?P<assessment>\d+)/(?P<slug>[\w-]+)/update/$',
        views.DataPivotUpdateSettings.as_view(), name='update'),
    url(r'^assessment/(?P<assessment>\d+)/(?P<slug>[\w-]+)/query-update/$',
        views.DataPivotUpdateQuery.as_view(), name='query-update'),
    url(r'^assessment/(?P<assessment>\d+)/(?P<slug>[\w-]+)/file-update/$',
        views.DataPivotUpdateFile.as_view(), name='file-update'),

    url(r'^assessment/(?P<assessment>\d+)/(?P<slug>[\w-]+)/delete/$',
        views.DataPivotDelete.as_view(), name='delete'),

    url(r'^excel-unicode-saving/$',
        views.ExcelUnicode.as_view(), name="excel-unicode")
)
