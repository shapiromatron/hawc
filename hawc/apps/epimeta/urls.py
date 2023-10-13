from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"assessment", api.EpiMetaAssessmentViewSet, basename="assessment")
router.register(r"protocol", api.MetaProtocol, basename="protocol")
router.register(r"result", api.MetaResult, basename="result")


app_name = "meta"
urlpatterns = [
    # API
    path("api/", include((router.urls, "api"))),
    # protocol views
    path(
        "study/<int:pk>/protocol/create/",
        views.MetaProtocolCreate.as_view(),
        name="protocol_create",
    ),
    path(
        "protocol/<int:pk>/",
        views.MetaProtocolDetail.as_view(),
        name="protocol_detail",
    ),
    path(
        "protocol/<int:pk>/update/",
        views.MetaProtocolUpdate.as_view(),
        name="protocol_update",
    ),
    path(
        "protocol/<int:pk>/delete/",
        views.MetaProtocolDelete.as_view(),
        name="protocol_delete",
    ),
    # result views
    path(
        "assessment/<int:pk>/results/",
        views.MetaResultFilterList.as_view(),
        name="result_list",
    ),
    path(
        "protocol/<int:pk>/result/create/",
        views.MetaResultCreate.as_view(),
        name="result_create",
    ),
    path(
        "protocol/<int:pk>/result/copy-as-new-selector/",
        views.MetaResultCopyAsNew.as_view(),
        name="result_copy_selector",
    ),
    path("result/<int:pk>/", views.MetaResultDetail.as_view(), name="result_detail"),
    path(
        "result/<int:pk>/update/",
        views.MetaResultUpdate.as_view(),
        name="result_update",
    ),
    path(
        "result/<int:pk>/delete/",
        views.MetaResultDelete.as_view(),
        name="result_delete",
    ),
]
