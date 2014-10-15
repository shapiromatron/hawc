from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    # BMD create/read/update views
    url(r'model/(?P<pk>[\d\.]+)/edit/$',
        views.BMDCreate.as_view(), name='edit'),

    url(r'model/(?P<pk>[\d\.]+)/select/$',
        views.BMDSelectionUpdate.as_view(), name='select'),

    url(r'model/(?P<pk>[\d\.]+)/view/$',
        views.BMDRead.as_view(), name='read'),

    url(r'model/(?P<pk>[\d\.]+)/versions/$',
        views.BMDVersions.as_view(), name='versions'),

    # BMD template JSON helper-functions
    url(r'model/(?P<pk>[\d\.]+)/template/$',
        views.getEndpointTemplate.as_view(), name='template'),

    url(r'(?P<vbmds>[\w\.]+)/models/(?P<datatype>[\w\.]+)/$',
        views.getDefaultOptions.as_view(), name='options'),

    url(r'(?P<vbmds>[\w\.]+)/model_option/(?P<datatype>[\w\.]+)/(?P<model_name>[-\w]+)/$',
        views.getSingleModelOption.as_view(), name='option'),

    # BMD assessment-level settings
    url(r'^assessment/(?P<pk>\d+)/settings/$',
        views.AssessSettingsRead.as_view(), name='assess_settings_detail'),

    url(r'^assessment/(?P<pk>\d+)/settings/edit/$',
        views.AssessSettingsUpdate.as_view(), name='assess_settings_update'),

    url(r'^assessment/(?P<pk>\d+)/logic/edit/$',
        views.AssessLogicUpdate.as_view(), name='assess_logic_update')
)
