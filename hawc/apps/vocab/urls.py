from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"ehv", api.EhvTermViewset, basename="ehv")

app_name = "vocab"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    path("ehv/", views.EhvBrowse.as_view(), name="ehv-browse"),
    path("comment/create/", views.CreateComment.as_view(), name="create_comment"),
    path("comments/", views.CommentList.as_view(), name="comments"),
    path("entity-terms/", views.EntityTermList.as_view(), name="entity-terms"),
    path("terms/", views.TermList.as_view(), name="terms"),
    path("proposed/", views.ProposedEntityTermList.as_view(), name="proposed"),
]

admin.autodiscover()
