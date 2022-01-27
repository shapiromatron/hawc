from django.urls import path

from . import views

app_name = "epiv2"
urlpatterns = [
    path("design/<int:pk>/create/", views.DesignCreate.as_view(), name="des_create",),
    path("design/<int:pk>/update/", views.DesignUpdate.as_view(), name="des_update",),
    path("design/<int:pk>/", views.DesignDetail.as_view(), name="des_detail",),
]
