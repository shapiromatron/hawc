from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.EpiMetaAssessmentViewset, base_name="assessment")
router.register(r"protocol", api.MetaProtocol, base_name="protocol")
router.register(r"result", api.MetaResult, base_name="result")


app_name = "meta"
urlpatterns = [
    # API
    url(r"^api/", include(router.urls, namespace="api")),
    # protocol views
    url(
        r"^study/(?P<pk>\d+)/protocol/create/$",
        views.MetaProtocolCreate.as_view(),
        name="protocol_create",
    ),
    url(r"^protocol/(?P<pk>\d+)/$", views.MetaProtocolDetail.as_view(), name="protocol_detail",),
    url(
        r"^protocol/(?P<pk>\d+)/update/$",
        views.MetaProtocolUpdate.as_view(),
        name="protocol_update",
    ),
    url(
        r"^protocol/(?P<pk>\d+)/delete/$",
        views.MetaProtocolDelete.as_view(),
        name="protocol_delete",
    ),
    # result views
    url(r"^assessment/(?P<pk>\d+)/results/$", views.MetaResultList.as_view(), name="result_list",),
    url(
        r"^protocol/(?P<pk>\d+)/result/create/$",
        views.MetaResultCreate.as_view(),
        name="result_create",
    ),
    url(
        r"^protocol/(?P<pk>\d+)/result/copy-as-new-selector/$",
        views.MetaResultCopyAsNew.as_view(),
        name="result_copy_selector",
    ),
    url(r"^result/(?P<pk>\d+)/$", views.MetaResultDetail.as_view(), name="result_detail"),
    url(r"^result/(?P<pk>\d+)/update/$", views.MetaResultUpdate.as_view(), name="result_update",),
    url(r"^result/(?P<pk>\d+)/delete/$", views.MetaResultDelete.as_view(), name="result_delete",),
]
