from django.urls import include, path
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
    path("<int:pk>/add-details/", views.StudyCreateFromReference.as_view(), name="new_study"),
    path("assessment/<int:pk>/new-study/", views.ReferenceStudyCreate.as_view(), name="new_ref"),
    path("assessment/<int:pk>/copy-studies/", views.StudiesCopy.as_view(), name="studies_copy"),
    path("<int:pk>/", views.StudyRead.as_view(), name="detail"),
    path("<int:pk>/toggle-lock/", views.StudyToggleLock.as_view(), name="toggle-lock"),
    path("<int:pk>/update/", views.StudyUpdate.as_view(), name="update"),
    path("<int:pk>/delete/", views.StudyDelete.as_view(), name="delete"),
    path("<int:pk>/risk-of-bias/", views.StudyRoBRedirect.as_view(), name="rob_redirect"),
    # attachment
    path("attachment/<int:pk>/", views.AttachmentRead.as_view(), name="attachment_detail"),
    path("<int:pk>/attachment/add/", views.AttachmentCreate.as_view(), name="attachment_create"),
    path("attachment/<int:pk>/delete/", views.AttachmentDelete.as_view(), name="attachment_delete"),
]
