from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.EpiMetaAssessmentViewset, basename="assessment")
router.register(r"protocol", api.MetaProtocol, basename="protocol")
router.register(r"result", api.MetaResult, basename="result")


app_name = "meta"
urlpatterns = [
    # API
    re_path(r"^api/", include((router.urls, "api"))),
    # protocol views
    re_path(
        r"^study/(?P<pk>\d+)/protocol/create/$",
        views.MetaProtocolCreate.as_view(),
        name="protocol_create",
    ),
    re_path(
        r"^protocol/(?P<pk>\d+)/$", views.MetaProtocolDetail.as_view(), name="protocol_detail",
    ),
    re_path(
        r"^protocol/(?P<pk>\d+)/update/$",
        views.MetaProtocolUpdate.as_view(),
        name="protocol_update",
    ),
    re_path(
        r"^protocol/(?P<pk>\d+)/delete/$",
        views.MetaProtocolDelete.as_view(),
        name="protocol_delete",
    ),
    # result views
    re_path(
        r"^assessment/(?P<pk>\d+)/results/$", views.MetaResultList.as_view(), name="result_list",
    ),
    re_path(
        r"^protocol/(?P<pk>\d+)/result/create/$",
        views.MetaResultCreate.as_view(),
        name="result_create",
    ),
    re_path(
        r"^protocol/(?P<pk>\d+)/result/copy-as-new-selector/$",
        views.MetaResultCopyAsNew.as_view(),
        name="result_copy_selector",
    ),
    re_path(r"^result/(?P<pk>\d+)/$", views.MetaResultDetail.as_view(), name="result_detail"),
    re_path(
        r"^result/(?P<pk>\d+)/update/$", views.MetaResultUpdate.as_view(), name="result_update",
    ),
    re_path(
        r"^result/(?P<pk>\d+)/delete/$", views.MetaResultDelete.as_view(), name="result_delete",
    ),
]
