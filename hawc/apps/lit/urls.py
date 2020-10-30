from django.urls import include, re_path
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
    re_path(r"^assessment/(?P<pk>\d+)/$", views.LitOverview.as_view(), name="overview"),
    # CRUD tags
    re_path(r"^assessment/tags/json/$", views.TagsJSON.as_view(), name="tags_list"),
    re_path(
        r"^assessment/(?P<pk>\d+)/tags/update/$", views.TagsUpdate.as_view(), name="tags_update",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/tags/update/copy/$", views.TagsCopy.as_view(), name="tags_copy",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/update/$",
        views.LiteratureAssessmentUpdate.as_view(),
        name="literature_assessment_update",
    ),
    # Reference-level details
    re_path(r"^reference/(?P<pk>\d+)/$", views.RefDetail.as_view(), name="ref_detail"),
    re_path(r"^reference/(?P<pk>\d+)/edit/$", views.RefEdit.as_view(), name="ref_edit"),
    re_path(r"^reference/(?P<pk>\d+)/delete/$", views.RefDelete.as_view(), name="ref_delete"),
    re_path(
        r"^reference/(?P<pk>\d+)/tag/$", views.TagByReference.as_view(), name="reference_tags_edit",
    ),
    re_path(r"^tag/(?P<pk>\d+)/tag/$", views.TagByTag.as_view(), name="references_tags_edit"),
    re_path(
        r"^assessment/(?P<pk>\d+)/tag/untagged/$",
        views.TagByUntagged.as_view(),
        name="tag_untagged",
    ),
    re_path(r"^assessment/(?P<pk>\d+)/references/$", views.RefList.as_view(), name="ref_list",),
    re_path(
        r"^assessment/(?P<pk>\d+)/references/extraction-ready/$",
        views.RefListExtract.as_view(),
        name="ref_list_extract",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/references/visualization/$",
        views.RefVisualization.as_view(),
        name="ref_visual",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/references/topic-model/$",
        views.RefTopicModel.as_view(),
        name="topic_model",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/references/search/$",
        views.RefSearch.as_view(),
        name="ref_search",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/references/(?P<tag_id>(\d+|untagged))/json/$",
        views.RefsByTagJSON.as_view(),
        name="refs_json",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/references/upload/$",
        views.RefUploadExcel.as_view(),
        name="ref_upload",
    ),
    # CRUD searches
    re_path(r"^assessment/(?P<pk>\d+)/searches/$", views.SearchList.as_view(), name="search_list",),
    re_path(r"^assessment/(?P<pk>\d+)/search/new/$", views.SearchNew.as_view(), name="search_new",),
    re_path(
        r"^assessment/(?P<pk>\d+)/search/copy/$",
        views.SearchCopyAsNewSelector.as_view(),
        name="copy_search",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/$",
        views.SearchDetail.as_view(),
        name="search_detail",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/update/$",
        views.SearchUpdate.as_view(),
        name="search_update",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/delete/$",
        views.SearchDelete.as_view(),
        name="search_delete",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/query/$",
        views.SearchQuery.as_view(),
        name="search_query",
    ),
    # CRUD import
    re_path(r"^assessment/(?P<pk>\d+)/import/new/$", views.ImportNew.as_view(), name="import_new",),
    re_path(
        r"^assessment/(?P<pk>\d+)/ris-import/new/$",
        views.ImportRISNew.as_view(),
        name="import_ris_new",
    ),
    # Edit tags
    re_path(
        r"^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/tag/$",
        views.TagBySearch.as_view(),
        name="search_tags_edit",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/tags/$",
        views.SearchRefList.as_view(),
        name="search_tags",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/tags-visuals/$",
        views.SearchTagsVisualization.as_view(),
        name="search_tags_visual",
    ),
    re_path(
        r"^ris-export-instructions/$",
        views.RISExportInstructions.as_view(),
        name="ris_export_instructions",
    ),
    re_path(r"^api/", include((router.urls, "api"))),
]
