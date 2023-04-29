from django.urls import path

from . import views

app_name = "mgmt"
urlpatterns = [
    # user task-list
    path("my-assignments/", views.UserAssignments.as_view(), name="user_assignments"),
    path(
        "my-assignments/<int:pk>/",
        views.UserAssessmentAssignments.as_view(),
        name="user_assessment_assignments",
    ),
    # assessment-level views
    path(
        "assessment/<int:pk>/",
        views.TaskDashboard.as_view(),
        name="assessment_dashboard",
    ),
    path(
        "assessment/<int:pk>/details/",
        views.TaskList.as_view(),
        name="task-list",
    ),
    # task htmx ViewSet
    path(
        "task/<int:pk>/",
        views.TaskViewSet.as_view(),
        {"action": "read"},
        name="task-detail",
    ),
    path(
        "taskv/<int:pk>/update/",
        views.TaskViewSet.as_view(),
        {"action": "update"},
        name="task-update",
    ),
]
