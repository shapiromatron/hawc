from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "assessmentvalues"
urlpatterns = [
    path("<int:pk>/new/", views.AssessmentValuesCreate.as_view(), name="values-create"),
    path("<int:pk>/", views.AssessmentValuesDetail.as_view(), name="values-detail"),
    path("<int:pk>/update/", views.AssessmentValuesUpdate.as_view(), name="values-update"),
    path("<int:pk>/delete/", views.AssessmentValuesDelete.as_view(), name="values-delete"),
]
