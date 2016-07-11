from django.conf.urls import url
from django.contrib import admin

from . import views

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
    url(r'^(?P<pk>\d+)/versions/$',
        views.AssessmentVersions.as_view(),
        name='versions'),
    url(r'^(?P<pk>\d+)/reports/$',
        views.AssessmentReports.as_view(),
        name='reports'),
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

    # report-template objects
    url(r'^(?P<pk>\d+)/templates/$',
        views.ReportTemplateList.as_view(),
        name='template_list'),
    url(r'^(?P<pk>\d+)/templates/create/$',
        views.ReportTemplateCreate.as_view(),
        name='template_create'),
    url(r'^templates/(?P<pk>\d+)/$',
        views.ReportTemplateDetail.as_view(),
        name='template_detail'),
    url(r'^templates/(?P<pk>\d+)/edit/$',
        views.ReportTemplateUpdate.as_view(),
        name='template_update'),
    url(r'^templates/(?P<pk>\d+)/delete/$',
        views.ReportTemplateDelete.as_view(),
        name='template_delete'),

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

    # api views
    url(r'^api/endpoints/$',
        views.AssessmentEndpointList.as_view({'get': 'list'}),
        name='endpoint_type_list'),
]

admin.autodiscover()
