from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import api, views


router = DefaultRouter()


urlpatterns = [
    url(r'^api/', include(router.urls)),

    # BMD assessment-level settings
    url(r'^assessment/(?P<pk>\d+)/settings/$',
        views.AssessSettingsRead.as_view(),
        name='assess_settings_detail'),

    url(r'^assessment/(?P<pk>\d+)/settings/edit/$',
        views.AssessSettingsUpdate.as_view(),
        name='assess_settings_update'),

    url(r'^assessment/(?P<pk>\d+)/logic/edit/$',
        views.AssessLogicUpdate.as_view(),
        name='assess_logic_update'),

    # BMD create/read/update views

    # BMD template JSON helper-functions

]
