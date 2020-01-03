from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views, api


router = DefaultRouter()
router.register(r'tags', api.ReferenceFilterTag, base_name="tags")
router.register(r'reference-cleanup', api.ReferenceCleanup, base_name="reference-cleanup")

urlpatterns = [

    # overview
    url(r'^assessment/(?P<pk>\d+)/$',
        views.LitOverview.as_view(),
        name='overview'),

    # CRUD tags
    url(r'^assessment/tags/json/$',
        views.TagsJSON.as_view(),
        name='tags_list'),
    url(r'^assessment/(?P<pk>\d+)/tags/update/$',
        views.TagsUpdate.as_view(),
        name='tags_update'),
    url(r'^assessment/(?P<pk>\d+)/tags/update/copy/$',
        views.TagsCopy.as_view(),
        name='tags_copy'),

    # Reference-level details
    url(r'^reference/(?P<pk>\d+)/$',
        views.RefDetail.as_view(),
        name='ref_detail'),
    url(r'^reference/(?P<pk>\d+)/edit/$',
        views.RefEdit.as_view(),
        name='ref_edit'),
    url(r'^reference/(?P<pk>\d+)/tag/$',
        views.TagByReference.as_view(),
        name='reference_tags_edit'),
    url(r'^tag/(?P<pk>\d+)/tag/$',
        views.TagByTag.as_view(),
        name='references_tags_edit'),
    url(r'^assessment/(?P<pk>\d+)/tag/untagged/$',
        views.TagByUntagged.as_view(),
        name='tag_untagged'),
    url(r'^assessment/(?P<pk>\d+)/references/$',
        views.RefList.as_view(),
        name='ref_list'),
    url(r'^assessment/(?P<pk>\d+)/references/extraction-ready/$',
        views.RefListExtract.as_view(),
        name='ref_list_extract'),
    url(r'^assessment/(?P<pk>\d+)/references/visualization/$',
        views.RefVisualization.as_view(),
        name='ref_visual'),
    url(r'^assessment/(?P<pk>\d+)/references/search/$',
        views.RefSearch.as_view(),
        name='ref_search'),
    url(r'^assessment/(?P<pk>\d+)/references/(?P<tag_id>(\d+|untagged))/json/$',
        views.RefsByTagJSON.as_view(),
        name='refs_json'),
    url(r'^assessment/(?P<pk>\d+)/references/download/$',
        views.RefDownloadExcel.as_view(),
        name='ref_download_excel'),
    url(r'^assessment/(?P<pk>\d+)/references/upload/$',
        views.RefUploadExcel.as_view(),
        name='ref_upload'),

    # CRUD searches
    url(r'^assessment/(?P<pk>\d+)/searches/$',
        views.SearchList.as_view(),
        name='search_list'),
    url(r'^assessment/(?P<pk>\d+)/search/new/$',
        views.SearchNew.as_view(),
        name='search_new'),
    url(r'^assessment/(?P<pk>\d+)/search/copy/$',
        views.SearchCopyAsNewSelector.as_view(),
        name='copy_search'),
    url(r'^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/$',
        views.SearchDetail.as_view(),
        name='search_detail'),
    url(r'^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/update/$',
        views.SearchUpdate.as_view(),
        name='search_update'),
    url(r'^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/delete/$',
        views.SearchDelete.as_view(),
        name='search_delete'),
    url(r'^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/query/$',
        views.SearchQuery.as_view(),
        name='search_query'),
    url(r'^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/download/$',
        views.SearchDownloadExcel.as_view(),
        name='search_download_excel'),

    # CRUD import
    url(r'^assessment/(?P<pk>\d+)/import/new/$',
        views.ImportNew.as_view(),
        name='import_new'),
    url(r'^assessment/(?P<pk>\d+)/ris-import/new/$',
        views.ImportRISNew.as_view(),
        name='import_ris_new'),

    # Edit tags
    url(r'^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/tag/$',
        views.TagBySearch.as_view(),
        name='search_tags_edit'),
    url(r'^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/tags/$',
        views.SearchRefList.as_view(),
        name='search_tags'),
    url(r'^assessment/(?P<pk>\d+)/search/(?P<slug>[\w-]+)/tags-visuals/$',
        views.SearchTagsVisualization.as_view(),
        name='search_tags_visual'),

    url(r'^ris-export-instructions/$',
        views.RISExportInstructions.as_view(),
        name='ris_export_instructions'),

    url(r'^api/', include(router.urls, namespace='api')),
]
