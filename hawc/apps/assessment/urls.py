from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register("assessment", api.Assessment, basename="assessment")
router.register("detail", api.AssessmentDetailViewSet, basename="detail")
router.register("value", api.AssessmentValueViewSet, basename="value")
router.register("dataset", api.DatasetViewSet, basename="dataset")
router.register("dsstox", api.DssToxViewSet, basename="dsstox")
router.register("strain", api.StrainViewSet, basename="strain")
router.register("effect-tag", api.EffectTagViewSet, basename="effect-tag")


app_name = "assessment"
urlpatterns = [
    # assessment objects
    path("all/", views.AssessmentFullList.as_view(), name="full_list"),
    path("public/", views.AssessmentPublicList.as_view(), name="public_list"),
    path("new/", views.AssessmentCreate.as_view(), name="new"),
    path("<int:pk>/", views.AssessmentDetail.as_view(), name="detail"),
    path("<int:pk>/update/", views.AssessmentUpdate.as_view(), name="update"),
    path(
        "<int:pk>/enabled-modules/update/",
        views.AssessmentModulesUpdate.as_view(),
        name="modules_update",
    ),
    path("<int:pk>/delete/", views.AssessmentDelete.as_view(), name="delete"),
    path(
        "<int:pk>/downloads/",
        views.AssessmentDownloads.as_view(),
        name="downloads",
    ),
    path(
        "<int:pk>/logs/",
        views.AssessmentLogList.as_view(),
        name="assessment_logs",
    ),
    path("<int:pk>/clear-cache/", views.AssessmentClearCache.as_view(), name="clear_cache"),
    # assessment details
    path(
        "details/<int:pk>/new/",
        views.AssessmentDetailCreate.as_view(),
        name="details-create",
    ),
    path(
        "details/<int:pk>/update/",
        views.AssessmentDetailUpdate.as_view(),
        name="details-update",
    ),
    # assessment values
    path("values/<int:pk>/new/", views.AssessmentValueCreate.as_view(), name="values-create"),
    path("values/<int:pk>/", views.AssessmentValueDetail.as_view(), name="values-detail"),
    path("values/<int:pk>/update/", views.AssessmentValueUpdate.as_view(), name="values-update"),
    path("values/<int:pk>/delete/", views.AssessmentValueDelete.as_view(), name="values-delete"),
    # log object
    path(
        "log/<int:content_type>/<int:object_id>/",
        views.LogObjectList.as_view(),
        name="log_object_list",
    ),
    path(
        "log/<int:pk>/",
        views.LogDetail.as_view(),
        name="log_detail",
    ),
    # attachment objects
    path(
        "attachment/<int:pk>/<slug:action>/",
        views.AttachmentViewSet.as_view(),
        name="attachment-htmx",
    ),
    # dataset
    path("<int:pk>/dataset/create/", views.DatasetCreate.as_view(), name="dataset_create"),
    path("dataset/<int:pk>/", views.DatasetDetail.as_view(), name="dataset_detail"),
    path("dataset/<int:pk>/update/", views.DatasetUpdate.as_view(), name="dataset_update"),
    path("dataset/<int:pk>/delete/", views.DatasetDelete.as_view(), name="dataset_delete"),
    # species
    path(
        "assessment/<int:pk>/species/create/",
        views.SpeciesCreate.as_view(),
        name="species_create",
    ),
    # strain
    path(
        "assessment/<int:pk>/strain/create/",
        views.StrainCreate.as_view(),
        name="strain_create",
    ),
    # dose units
    path(
        "assessment/<int:pk>/dose-units/create/",
        views.DoseUnitsCreate.as_view(),
        name="dose_units_create",
    ),
    # dtxsid
    path(
        "dtxsid/create/",
        views.DSSToxCreate.as_view(),
        name="dtxsid_create",
    ),
    # endpoint objects
    path(
        "<int:pk>/endpoints/",
        views.BaseEndpointList.as_view(),
        name="endpoint_list",
    ),
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
    # helper functions
    path("content-types/", views.AboutContentTypes.as_view(), name="content_types"),
    path("close-window/", views.CloseWindow.as_view(), name="close_window"),
    # assessment level study
    path(
        "<int:pk>/clean-study-metrics/",
        views.CleanStudyRoB.as_view(),
        name="clean_study_metrics",
    ),
    # published items
    path(
        "<int:pk>/published/",
        views.PublishedItemsChecklist.as_view(),
        {"action": "list"},
        name="bulk-publish",
    ),
    path(
        "<int:pk>/published/<str:type>/<int:object_id>/",
        views.PublishedItemsChecklist.as_view(),
        {"action": "update_item"},
        name="publish-update",
    ),
    # assessment labels
    path(
        "<int:pk>/labeled-items/",
        views.LabeledItemList.as_view(),
        name="labeled-items",
    ),
    path(
        "<int:pk>/labels/",
        views.LabelList.as_view(),
        name="manage-labels",
    ),
    path(
        "label/<int:pk>/<slug:action>/",
        views.LabelViewSet.as_view(),
        name="label-htmx",
    ),
    path(
        "label-item/<int:content_type>/<int:object_id>/",
        views.LabelItem.as_view(),
        name="label-item",
    ),
    path(
        "trained-model/create/",
        views.TrainedModelCreate.as_view(),
        name="trained_model_create",
    ),
    path(
        "trained-model/update/<int:pk>",
        views.TrainedModelUpdate.as_view(),
        name="trained_model_update",
    ),
    path(
        "trained-model/<int:pk>/",
        views.TrainedModelDetail.as_view(),
        name="trained_model_detail",
    ),
    path(
        "trained-models/",
        views.TrainedModelList.as_view(),
        name="trained_model_list",
    ),
    path(
        "trained-models/<int:pk>/prediction-class/create/",
        views.PredictionClassCreate.as_view(),
        name="prediction_class_create",
    ),
    # api views
    path("api/", include((router.urls, "api"))),
]

admin.autodiscover()
