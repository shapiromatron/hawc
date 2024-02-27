from django.urls import path

from . import views

app_name = "mgmt"
urlpatterns = [
    # user task-list
    path("tasks/", views.UserTaskList.as_view(), name="user-task-list"),
    path(
        "assessment/<int:pk>/tasks/",
        views.UserAssessmentTaskList.as_view(),
        name="user-assessment-task-list",
    ),
    # assessment-level views
    path(
        "assessment/<int:pk>/",
        views.AssessmentTaskDashboard.as_view(),
        name="task-dashboard",
    ),
    path(
        "assessment/<int:pk>/details/",
        views.AssessmentTaskList.as_view(),
        name="task-list",
    ),
    # task htmx ViewSet
    path(
        "task/<int:pk>/<slug:action>/",
        views.TaskViewSet.as_view(),
        name="task-htmx",
    ),
    path(
        "assessment/<int:pk>/analytics/",
        views.AssessmentAnalytics.as_view(),
        name="assessment-analytics",
    ),
]
