from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register("assessment", api.MgmtViewSet, basename="assessment")

app_name = "mgmt"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    # user task-list
    path("tasks/", views.UserTaskList.as_view(), name="user-task-list"),
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
    path(
        "assessment/<int:pk>/task-setup/",
        views.TaskSetupList.as_view(),
        name="task-setup-list",
    ),
    path("assessment/<int:pk>/copy/", views.TaskSetupCopy.as_view(), name="task-setup-copy"),
    # task setup htmx viewsets
    path(
        "type/<int:pk>/<slug:action>/",
        views.TaskTypeViewSet.as_view(),
        name="task-type-htmx",
    ),
    path(
        "trigger/<int:pk>/<slug:action>/",
        views.TaskTriggerViewSet.as_view(),
        name="task-trigger-htmx",
    ),
    path(
        "status/<int:pk>/<slug:action>/",
        views.TaskStatusViewSet.as_view(),
        name="task-status-htmx",
    ),
]
