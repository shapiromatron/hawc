from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

app_name = "animalv2"
urlpatterns = [
    path(
        "study/<int:pk>/study-level-values/",
        views.StudyLevelValues.as_view(),
        name="studylevelvalues",
    ),
    path(
        "study-level-values/<int:pk>/<slug:action>/",
        views.StudyLevelValueViewSet.as_view(),
        name="studylevelvalues-htmx",
    ),
]
