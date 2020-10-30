from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"task", api.TaskViewSet, basename="task")

app_name = "mgmt"
urlpatterns = [
    re_path(r"^api/", include((router.urls, "api"))),
    # user task-list
    re_path(r"^my-assignments/$", views.UserAssignments.as_view(), name="user_assignments"),
    re_path(
        r"^my-assignments/(?P<pk>\d+)/$",
        views.UserAssessmentAssignments.as_view(),
        name="user_assessment_assignments",
    ),
    # assessment-level views
    re_path(
        r"^assessment/(?P<pk>\d+)/$", views.TaskDashboard.as_view(), name="assessment_dashboard",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/details/$", views.TaskDetail.as_view(), name="assessment_tasks",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/edit/$", views.TaskModify.as_view(), name="assessment_modify",
    ),
]
