from django.contrib import admin
from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"ehv", api.EhvTermViewset, basename="ehv")

app_name = "vocab"
urlpatterns = [
    re_path(r"^api/", include((router.urls, "api"))),
    re_path(r"^ehv/$", views.EhvBrowse.as_view(), name="ehv-browse"),
    re_path(r"^comment/create/$", views.CreateComment.as_view(), name="create_comment"),
    re_path(r"^comments/$", views.CommentList.as_view(), name="comments"),
    re_path(r"^entity-terms/$", views.EntityTermList.as_view(), name="entity-terms"),
    re_path(r"^terms/$", views.TermList.as_view(), name="terms"),
    re_path(r"^proposed/$", views.ProposedEntityTermList.as_view(), name="proposed"),
]

admin.autodiscover()
