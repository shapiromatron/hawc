from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from . import views, api

router = DefaultRouter()
router.register(r'assessment', api.Assessment, base_name='assessment')
router.register(r'endpoints', api.AssessmentEndpointList, base_name='endpoint_type')

urlpatterns = [

    # assessment objects
    url(r'^all/$',
        views.AssessmentFullList.as_view(),
        name='full_list'),
    url(r'^public/$',
        views.AssessmentPublicList.as_view(),
        name='public_list'),
    url(r'^new/$',
        views.AssessmentCreate.as_view(),
        name='new'),
    url(r'^(?P<pk>\d+)/$',
        views.AssessmentRead.as_view(),
        name='detail'),
    url(r'^(?P<pk>\d+)/edit/$',
        views.AssessmentUpdate.as_view(),
        name='update'),
    url(r'^(?P<pk>\d+)/enabled-modules/edit/$',
        views.AssessmentModulesUpdate.as_view(),
        name='modules_update'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.AssessmentDelete.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/downloads/$',
        views.AssessmentDownloads.as_view(),
        name='downloads'),
    url(r'^(?P<pk>\d+)/email-project-managers/$',
        views.AssessmentEmailManagers.as_view(),
        name='email_managers'),

    # attachment objects
    url(r'^(?P<pk>\d+)/attachment/create/$',
        views.AttachmentCreate.as_view(),
        name='attachment_create'),
    url(r'^attachment/(?P<pk>\d+)/$',
        views.AttachmentRead.as_view(),
        name='attachment_detail'),
    url(r'^attachment/(?P<pk>\d+)/update/$',
        views.AttachmentUpdate.as_view(),
        name='attachment_update'),
    url(r'^attachment/(?P<pk>\d+)/delete/$',
        views.AttachmentDelete.as_view(),
        name='attachment_delete'),

    # species
    url(r'^assessment/(?P<pk>\d+)/species/create/$',
        views.SpeciesCreate.as_view(),
        name='species_create'),

    # strain
    url(r'^strains/',
        views.getStrains.as_view(),
        name='get_strains'),
    url(r'^assessment/(?P<pk>\d+)/strain/create/$',
        views.StrainCreate.as_view(),
        name='strain_create'),

    # dose units
    url(r'^assessment/(?P<pk>\d+)/dose-units/create/$',
        views.DoseUnitsCreate.as_view(),
        name='dose_units_create'),

    # endpoint objects
    url(r'^(?P<pk>\d+)/endpoints/$',
        views.BaseEndpointList.as_view(),
        name='endpoint_list'),
    url(r'^(?P<pk>\d+)/clean-extracted-data/',
        views.CleanExtractedData.as_view(),
        name='clean_extracted_data'),
    url(r'^assessment/(?P<pk>\d+)/effect-tags/create/$',
        views.EffectTagCreate.as_view(),
        name='effect_tag_create'),

    # helper functions
    url(r'^cas-details/',
        views.CASDetails.as_view(),
        name='cas_details'),
    url(r'^download-plot/$',
        views.DownloadPlot.as_view(),
        name='download_plot'),
    url(r'^close-window/$',
        views.CloseWindow.as_view(),
        name='close_window'),

    # assessment level study
    url(r'^(?P<pk>\d+)/clean-study-metrics',
        views.CleanStudyRoB.as_view(),
        name='clean_study_metrics'),

    # api views
    url(r'^api/', include(router.urls, namespace='api')),

]

admin.autodiscover()
