from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.LiteratureAssessmentViewset, basename="assessment")
router.register(r"reference", api.ReferenceViewset, basename="reference")
router.register(r"search", api.SearchViewset, basename="search")
router.register(r"tags", api.ReferenceFilterTagViewset, basename="tags")
router.register(r"reference-cleanup", api.ReferenceCleanupViewset, basename="reference-cleanup")

app_name = "lit"
urlpatterns = [
    # overview
    path("assessment/<int:pk>/", views.LitOverview.as_view(), name="overview"),
    # CRUD tags
    path("assessment/<int:pk>/tags/update/", views.TagsUpdate.as_view(), name="tags_update",),
    path("assessment/<int:pk>/tags/update/copy/", views.TagsCopy.as_view(), name="tags_copy",),
    path(
        "assessment/<int:pk>/update/",
        views.LiteratureAssessmentUpdate.as_view(),
        name="literature_assessment_update",
    ),
    # Reference-level details
    path("reference/<int:pk>/", views.RefDetail.as_view(), name="ref_detail"),
    path("reference/<int:pk>/update/", views.RefEdit.as_view(), name="ref_edit"),
    path("reference/<int:pk>/delete/", views.RefDelete.as_view(), name="ref_delete"),
    path("reference/<int:pk>/tag/", views.TagByReference.as_view(), name="reference_tags_edit",),
    path("tag/<int:pk>/tag/", views.TagByTag.as_view(), name="references_tags_edit"),
    path("assessment/<int:pk>/tag/untagged/", views.TagByUntagged.as_view(), name="tag_untagged",),
    path("assessment/<int:pk>/tag/bulk/", views.BulkTagReferences.as_view(), name="bulk_tag",),
    path("assessment/<int:pk>/references/", views.RefList.as_view(), name="ref_list",),
    path(
        "assessment/<int:pk>/references/extraction-ready/",
        views.RefListExtract.as_view(),
        name="ref_list_extract",
    ),
    path(
        "assessment/<int:pk>/references/visualization/",
        views.RefVisualization.as_view(),
        name="ref_visual",
    ),
    path(
        "assessment/<int:pk>/references/topic-model/",
        views.RefTopicModel.as_view(),
        name="topic_model",
    ),
    path("assessment/<int:pk>/references/search/", views.RefSearch.as_view(), name="ref_search",),
    path(
        "assessment/<int:pk>/references/upload/", views.RefUploadExcel.as_view(), name="ref_upload",
    ),
    # CRUD searches
    path("assessment/<int:pk>/search/new/", views.SearchNew.as_view(), name="search_new",),
    path(
        "assessment/<int:pk>/search/copy/",
        views.SearchCopyAsNewSelector.as_view(),
        name="copy_search",
    ),
    path(
        "assessment/<int:pk>/search/<slug:slug>/",
        views.SearchDetail.as_view(),
        name="search_detail",
    ),
    path(
        "assessment/<int:pk>/search/<slug:slug>/update/",
        views.SearchUpdate.as_view(),
        name="search_update",
    ),
    path(
        "assessment/<int:pk>/search/<slug:slug>/delete/",
        views.SearchDelete.as_view(),
        name="search_delete",
    ),
    path(
        "assessment/<int:pk>/search/<slug:slug>/query/",
        views.SearchQuery.as_view(),
        name="search_query",
    ),
    # CRUD import
    path("assessment/<int:pk>/import/new/", views.ImportNew.as_view(), name="import_new",),
    path(
        "assessment/<int:pk>/ris-import/new/", views.ImportRISNew.as_view(), name="import_ris_new",
    ),
    # Edit tags
    path(
        "assessment/<int:pk>/search/<slug:slug>/tag/",
        views.TagBySearch.as_view(),
        name="search_tags_edit",
    ),
    path(
        "assessment/<int:pk>/search/<slug:slug>/tags/",
        views.SearchRefList.as_view(),
        name="search_tags",
    ),
    path(
        "assessment/<int:pk>/search/<slug:slug>/tags-visuals/",
        views.SearchTagsVisualization.as_view(),
        name="search_tags_visual",
    ),
    path(
        "ris-export-instructions/",
        views.RISExportInstructions.as_view(),
        name="ris_export_instructions",
    ),
    path("api/", include((router.urls, "api"))),
]
