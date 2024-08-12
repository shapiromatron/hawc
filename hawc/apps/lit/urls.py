from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"assessment", api.LiteratureAssessmentViewSet, basename="assessment")
router.register(r"reference", api.ReferenceViewSet, basename="reference")
router.register(r"search", api.SearchViewSet, basename="search")
router.register(r"tags", api.ReferenceFilterTagViewSet, basename="tags")

app_name = "lit"
urlpatterns = [
    # overview
    path("assessment/<int:pk>/", views.LitOverview.as_view(), name="overview"),
    # CRUD tags
    path(
        "assessment/<int:pk>/tags/update/",
        views.TagsUpdate.as_view(),
        name="tags_update",
    ),
    path(
        "assessment/<int:pk>/tags/update/copy/",
        views.TagsCopy.as_view(),
        name="tags_copy",
    ),
    path(
        "assessment/<int:pk>/update/",
        views.LiteratureAssessmentUpdate.as_view(),
        name="literature_assessment_update",
    ),
    path(
        "assessment/<int:pk>/venn/",
        views.VennView.as_view(),
        name="venn",
    ),
    # Reference-level details
    path("reference/<int:pk>/", views.RefDetail.as_view(), name="ref_detail"),
    path("reference/<int:pk>/update/", views.RefEdit.as_view(), name="ref_edit"),
    path("reference/<int:pk>/delete/", views.RefDelete.as_view(), name="ref_delete"),
    path(
        "reference/<int:pk>/tag-status/",
        views.ReferenceTagStatus.as_view(),
        name="tag-status",
    ),
    path(
        "assessment/<int:pk>/tag/",
        views.TagReferences.as_view(),
        name="tag",
    ),
    path(
        "assessment/<int:pk>/tag/bulk/",
        views.BulkTagReferences.as_view(),
        name="bulk_tag",
    ),
    path(
        "assessment/<int:pk>/references/",
        views.RefList.as_view(),
        name="ref_list",
    ),
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
        "assessment/<int:pk>/references/search/",
        views.RefFilterList.as_view(),
        name="ref_search",
    ),
    path(
        "assessment/<int:pk>/references/upload/",
        views.RefUploadExcel.as_view(),
        name="ref_upload",
    ),
    # CRUD searches
    path(
        "assessment/<int:pk>/search/create/",
        views.SearchNew.as_view(),
        name="search_new",
    ),
    path(
        "assessment/<int:pk>/search/copy/",
        views.SearchCopyForm.as_view(),
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
    path(
        "assessment/<int:pk>/import/create/",
        views.ImportNew.as_view(),
        name="import_new",
    ),
    path(
        "assessment/<int:pk>/ris-import/create/",
        views.ImportRISNew.as_view(),
        name="import_ris_new",
    ),
    # Edit tags
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
    path(
        "assessment/<int:pk>/reference-tag-conflicts/",
        views.ConflictResolution.as_view(),
        name="tag-conflicts",
    ),
    path(
        "assessment/<int:pk>/bulk-merge-conflicts/",
        views.BulkMerge.as_view(),
        name="bulk-merge-conflicts",
    ),
    path(
        "assessment/<int:pk>/user-tags/",
        views.UserTagList.as_view(),
        name="user-tag-list",
    ),
    path(
        "assessment/<int:pk>/workflows/",
        views.Workflows.as_view(),
        name="workflows",
    ),
    # workflow objects
    path(
        "workflows/<int:pk>/<slug:action>/",
        views.WorkflowViewSet.as_view(),
        name="workflow-htmx",
    ),
    path("api/", include((router.urls, "api"))),
]
