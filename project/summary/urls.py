from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^assessment/(?P<pk>\d+)/summaries/$',
        views.SummaryTextList.as_view(), name='list'),
    url(r'^assessment/(?P<pk>\d+)/summaries/modify/$',
        views.SummaryTextModify.as_view(), name='modify'),
    url(r'^assessment/(?P<pk>\d+)/summaries/json/$',
        views.SummaryTextJSON.as_view(), name='json'),
)
