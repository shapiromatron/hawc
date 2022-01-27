from django.urls import path

from . import views

app_name = "epiv2"
urlpatterns = [
    path("study/<int:pk>/design/create/", views.DesignCreate.as_view(), name="des_create",),
    path("design/<int:pk>/update/", views.DesignUpdate.as_view(), name="des_update",),
    path("design/<int:pk>/", views.DesignDetail.as_view(), name="des_detail",),
    path("design/<int:pk>/delete/", views.DesignDelete.as_view(), name="des_delete",),
]
