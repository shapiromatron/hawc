from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import api, views


router = DefaultRouter()
router.register(r'bmd', api.BMD_session, base_name="bmd")
router.register(r'bmd-model', api.BMD_model_run, base_name="bmd-model")


urlpatterns = [
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
        views.AssessLogicUpdate.as_view(), name='assess_logic_update'),

    url(r'^api/', include(router.urls))
]
