from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"ehv", api.EhvTermViewset, basename="ehv")

app_name = "vocab"
urlpatterns = [
    url(r"^api/", include((router.urls, "api"))),
    url(r"^ehv/$", views.EhvBrowse.as_view(), name="ehv-browse"),
    url(r"^comment/create/$", views.CreateComment.as_view(), name="create_comment"),
    url(r"^comments/$", views.CommentList.as_view(), name="comments"),
    url(r"^entity-terms/$", views.EntityTermList.as_view(), name="entity-terms"),
    url(r"^terms/$", views.TermList.as_view(), name="terms"),
    url(r"^proposed/$", views.ProposedEntityTermList.as_view(), name="proposed"),
]

admin.autodiscover()
