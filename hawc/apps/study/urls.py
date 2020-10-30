from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"study", api.Study, basename="study")
router.register(r"study-cleanup", api.StudyCleanupFieldsView, basename="study-cleanup")

app_name = "study"
urlpatterns = [
    re_path(r"^api/", include((router.urls, "api"))),
    # study
    re_path(r"^assessment/(?P<pk>\d+)/$", views.StudyList.as_view(), name="list"),
    re_path(
        r"^(?P<pk>\d+)/add-details/$", views.StudyCreateFromReference.as_view(), name="new_study",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/new-study/$",
        views.ReferenceStudyCreate.as_view(),
        name="new_ref",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/copy-studies/$", views.StudiesCopy.as_view(), name="studies_copy",
    ),
    re_path(r"^(?P<pk>\d+)/$", views.StudyRead.as_view(), name="detail"),
    re_path(r"^(?P<pk>\d+)/edit/$", views.StudyUpdate.as_view(), name="update"),
    re_path(r"^(?P<pk>\d+)/delete/$", views.StudyDelete.as_view(), name="delete"),
    re_path(r"^(?P<pk>\d+)/risk-of-bias/$", views.StudyRoBRedirect.as_view(), name="rob_redirect",),
    # attachment
    re_path(
        r"^attachment/(?P<pk>\d+)/$", views.AttachmentRead.as_view(), name="attachment_detail",
    ),
    re_path(
        r"^(?P<pk>\d+)/attachment/add/$",
        views.AttachmentCreate.as_view(),
        name="attachment_create",
    ),
    re_path(
        r"^attachment/(?P<pk>\d+)/delete/$",
        views.AttachmentDelete.as_view(),
        name="attachment_delete",
    ),
    re_path(
        r"^(?P<pk>\d+)/editability-update/(?P<updated_value>.*)/$",
        views.EditabilityUpdate.as_view(),
        name="editability_update",
    ),
]
