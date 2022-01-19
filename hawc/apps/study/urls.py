from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"study", api.Study, basename="study")
router.register(r"study-cleanup", api.StudyCleanupFieldsView, basename="study-cleanup")

app_name = "study"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    # study
    path("assessment/<int:pk>/", views.StudyList.as_view(), name="list"),
    path("<int:pk>/add-details/", views.StudyCreateFromReference.as_view(), name="new_study",),
    path("assessment/<int:pk>/new-study/", views.ReferenceStudyCreate.as_view(), name="new_ref",),
    path("assessment/<int:pk>/copy-studies/", views.StudiesCopy.as_view(), name="studies_copy",),
    path("<int:pk>/", views.StudyRead.as_view(), name="detail"),
    path("<int:pk>/update/", views.StudyUpdate.as_view(), name="update"),
    path("<int:pk>/delete/", views.StudyDelete.as_view(), name="delete"),
    path("<int:pk>/risk-of-bias/", views.StudyRoBRedirect.as_view(), name="rob_redirect",),
    # attachment
    path("attachment/<int:pk>/", views.AttachmentRead.as_view(), name="attachment_detail",),
    path(
        "attachment/<int:pk>/create/",
        views.AttachmentViewset.as_view(),
        {"action": "create"},
        name="attachment-create",
    ),
    path(
        "attachment/<int:pk>/read/",
        views.AttachmentViewset.as_view(),
        {"action": "read"},
        name="attachment-read",
    ),
    path(
        "attachment/<int:pk>/delete/",
        views.AttachmentViewset.as_view(),
        {"action": "delete"},
        name="attachment-delete",
    ),
    path("<int:pk>/attachments/", views.AttachmentList.as_view(), name="attachment_list"),
    re_path(
        r"^(?P<pk>\d+)/editability-update/(?P<updated_value>.*)/$",
        views.EditabilityUpdate.as_view(),
        name="editability_update",
    ),
]
