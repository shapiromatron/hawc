from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"task", api.TaskViewSet, basename="task")

app_name = "mgmt"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    # user task-list
    path("my-assignments/", views.UserAssignments.as_view(), name="user_assignments"),
    path(
        "my-assignments/<int:pk>/",
        views.UserAssessmentAssignments.as_view(),
        name="user_assessment_assignments",
    ),
    # assessment-level views
    path("assessment/<int:pk>/", views.TaskDashboard.as_view(), name="assessment_dashboard",),
    path("assessment/<int:pk>/details/", views.TaskDetail.as_view(), name="assessment_tasks",),
    path("assessment/<int:pk>/update/", views.TaskModify.as_view(), name="assessment_modify",),
]
