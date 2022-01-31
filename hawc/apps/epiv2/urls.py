from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"design", api.Design, basename="design")

app_name = "epiv2"
urlpatterns = [
    path("api/", include((router.urls, "api"))),

    # Design (similar to Study Population object from epi version 1)
    path("study/<int:pk>/design/create/", views.DesignCreate.as_view(), name="design_create",),
    path("design/<int:pk>/update/", views.DesignUpdate.as_view(), name="design_update",),
    path("design/<int:pk>/", views.DesignDetail.as_view(), name="design_detail",),
    path("design/<int:pk>/delete/", views.DesignDelete.as_view(), name="design_delete",),
]
