from hawc.apps.assessment.api import BlogViewset
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.Assessment, basename="assessment")
router.register(r"dashboard", api.AdminDashboardViewset, basename="admin_dashboard")
router.register(r"dataset", api.DatasetViewset, basename="dataset")
router.register(r"blog", api.BlogViewset, basename="blog")

app_name = "assessment"
urlpatterns = [
    # assessment objects
    url(r"^all/$", views.AssessmentFullList.as_view(), name="full_list"),
    url(r"^public/$", views.AssessmentPublicList.as_view(), name="public_list"),
    url(r"^new/$", views.AssessmentCreate.as_view(), name="new"),
    url(r"^(?P<pk>\d+)/$", views.AssessmentRead.as_view(), name="detail"),
    url(r"^(?P<pk>\d+)/edit/$", views.AssessmentUpdate.as_view(), name="update"),
    url(
        r"^(?P<pk>\d+)/enabled-modules/edit/$",
        views.AssessmentModulesUpdate.as_view(),
        name="modules_update",
    ),
    url(r"^(?P<pk>\d+)/delete/$", views.AssessmentDelete.as_view(), name="delete"),
    url(r"^(?P<pk>\d+)/downloads/$", views.AssessmentDownloads.as_view(), name="downloads",),
    url(r"^(?P<pk>\d+)/clear-cache/$", views.AssessmentClearCache.as_view(), name="clear_cache"),
    # attachment objects
    url(
        r"^(?P<pk>\d+)/attachment/create/$",
        views.AttachmentCreate.as_view(),
        name="attachment_create",
    ),
    url(r"^attachment/(?P<pk>\d+)/$", views.AttachmentRead.as_view(), name="attachment_detail",),
    url(
        r"^attachment/(?P<pk>\d+)/update/$",
        views.AttachmentUpdate.as_view(),
        name="attachment_update",
    ),
    url(
        r"^attachment/(?P<pk>\d+)/delete/$",
        views.AttachmentDelete.as_view(),
        name="attachment_delete",
    ),
    # dataset
    url(r"^(?P<pk>\d+)/dataset/create/$", views.DatasetCreate.as_view(), name="dataset_create"),
    url(r"^dataset/(?P<pk>\d+)/$", views.DatasetRead.as_view(), name="dataset_detail"),
    url(r"^dataset/(?P<pk>\d+)/update/$", views.DatasetUpdate.as_view(), name="dataset_update"),
    url(r"^dataset/(?P<pk>\d+)/delete/$", views.DatasetDelete.as_view(), name="dataset_delete"),
    # species
    url(
        r"^assessment/(?P<pk>\d+)/species/create/$",
        views.SpeciesCreate.as_view(),
        name="species_create",
    ),
    # strain
    url(r"^strains/", views.getStrains.as_view(), name="get_strains"),
    url(
        r"^assessment/(?P<pk>\d+)/strain/create/$",
        views.StrainCreate.as_view(),
        name="strain_create",
    ),
    # dose units
    url(
        r"^assessment/(?P<pk>\d+)/dose-units/create/$",
        views.DoseUnitsCreate.as_view(),
        name="dose_units_create",
    ),
    # endpoint objects
    url(r"^(?P<pk>\d+)/endpoints/$", views.BaseEndpointList.as_view(), name="endpoint_list",),
    url(
        r"^(?P<pk>\d+)/clean-extracted-data/",
        views.CleanExtractedData.as_view(),
        name="clean_extracted_data",
    ),
    url(
        r"^assessment/(?P<pk>\d+)/effect-tags/create/$",
        views.EffectTagCreate.as_view(),
        name="effect_tag_create",
    ),
    # logs / blogs
    url(r"^blog/$", views.BlogList.as_view(), name="blog"),
    # helper functions
    url(
        r"^casrn/(?P<casrn>\d{1,7}-\d{1,3}-\d{1,2})/$", api.CasrnView.as_view(), name="casrn_detail"
    ),
    url(r"^download-plot/$", views.DownloadPlot.as_view(), name="download_plot"),
    url(r"^close-window/$", views.CloseWindow.as_view(), name="close_window"),
    # assessment level study
    url(
        r"^(?P<pk>\d+)/clean-study-metrics",
        views.CleanStudyRoB.as_view(),
        name="clean_study_metrics",
    ),
    # api views
    url(r"^api/", include((router.urls, "api"))),
]

admin.autodiscover()
