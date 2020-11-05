from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.Assessment, basename="assessment")
router.register(r"dashboard", api.AdminDashboardViewset, basename="admin_dashboard")
router.register(r"dataset", api.DatasetViewset, basename="dataset")
router.register(r"jobs", api.JobViewset, basename="jobs")
router.register(r"logs", api.LogViewset, basename="logs")
router.register(r"dsstox", api.DssToxViewset, basename="dsstox")


app_name = "assessment"
urlpatterns = [
    # assessment objects
    path("all/", views.AssessmentFullList.as_view(), name="full_list"),
    path("public/", views.AssessmentPublicList.as_view(), name="public_list"),
    path("new/", views.AssessmentCreate.as_view(), name="new"),
    path("<int:pk>/", views.AssessmentRead.as_view(), name="detail"),
    path("<int:pk>/edit/", views.AssessmentUpdate.as_view(), name="update"),
    path(
        "<int:pk>/enabled-modules/edit/",
        views.AssessmentModulesUpdate.as_view(),
        name="modules_update",
    ),
    path("<int:pk>/delete/", views.AssessmentDelete.as_view(), name="delete"),
    path("<int:pk>/downloads/", views.AssessmentDownloads.as_view(), name="downloads",),
    path("<int:pk>/clear-cache/", views.AssessmentClearCache.as_view(), name="clear_cache"),
    # attachment objects
    path(
        "<int:pk>/attachment/create/", views.AttachmentCreate.as_view(), name="attachment_create",
    ),
    path("attachment/<int:pk>/", views.AttachmentRead.as_view(), name="attachment_detail",),
    path(
        "attachment/<int:pk>/update/", views.AttachmentUpdate.as_view(), name="attachment_update",
    ),
    path(
        "attachment/<int:pk>/delete/", views.AttachmentDelete.as_view(), name="attachment_delete",
    ),
    # dataset
    path("<int:pk>/dataset/create/", views.DatasetCreate.as_view(), name="dataset_create"),
    path("dataset/<int:pk>/", views.DatasetRead.as_view(), name="dataset_detail"),
    path("dataset/<int:pk>/update/", views.DatasetUpdate.as_view(), name="dataset_update"),
    path("dataset/<int:pk>/delete/", views.DatasetDelete.as_view(), name="dataset_delete"),
    # species
    path(
        "assessment/<int:pk>/species/create/", views.SpeciesCreate.as_view(), name="species_create",
    ),
    # strain
    path("strains/", views.getStrains.as_view(), name="get_strains"),
    path("assessment/<int:pk>/strain/create/", views.StrainCreate.as_view(), name="strain_create",),
    # dose units
    path(
        "assessment/<int:pk>/dose-units/create/",
        views.DoseUnitsCreate.as_view(),
        name="dose_units_create",
    ),
    # dtxsid
    path("dtxsid/create/", views.DSSToxCreate.as_view(), name="dtxsid_create",),
    # endpoint objects
    path("<int:pk>/endpoints/", views.BaseEndpointList.as_view(), name="endpoint_list",),
    path(
        "<int:pk>/clean-extracted-data/",
        views.CleanExtractedData.as_view(),
        name="clean_extracted_data",
    ),
    path(
        "assessment/<int:pk>/effect-tags/create/",
        views.EffectTagCreate.as_view(),
        name="effect_tag_create",
    ),
    # logs / blogs
    path("blog/", views.BlogList.as_view(), name="blog"),
    # vocab
    path("<int:pk>/vocab/", views.VocabList.as_view(), name="vocab"),
    # helper functions
    path("download-plot/", views.DownloadPlot.as_view(), name="download_plot"),
    path("close-window/", views.CloseWindow.as_view(), name="close_window"),
    # assessment level study
    path(
        "<int:pk>/clean-study-metrics/", views.CleanStudyRoB.as_view(), name="clean_study_metrics",
    ),
    # api views
    path("api/", include((router.urls, "api"))),
]

admin.autodiscover()
