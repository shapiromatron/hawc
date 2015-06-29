from django.conf.urls import url

from . import views


urlpatterns = [

    url(r'^assessment/(?P<pk>\d+)/settings/$',
        views.CommentSettingsDetail.as_view(),
        name='comment_settings_details'),
    url(r'^assessment/(?P<pk>\d+)/settings/update/$',
        views.CommentSettingsUpdate.as_view(),
        name='comment_settings_update'),


    url(r'^(?P<content_type>[\w-]+)/(?P<object_id>\d+)/$',
        views.CommentList.as_view(),
        name='get_comments'),
    url(r'^(?P<content_type>[\w-]+)/(?P<object_id>\d+)/post/$',
        views.CommentCreate.as_view(),
        name='comment_create'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.CommentDelete.as_view(),
        name='comment_delete'),

    url(r'^assessment/(?P<pk>\d+)/all/$',
        views.CommentListAssessment.as_view(),
        name='comment_list_assessment'),
    url(r'^assessment/(?P<pk>\d+)/all/word/$',
        views.CommentReport.as_view(),
        name='comment_report'),
]
