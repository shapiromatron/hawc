from django.conf.urls import include, url

from ..common.api import OptionalTrailingSlashRouter
from . import api, views

router = OptionalTrailingSlashRouter()
router.register(r"task", api.Task, basename="task")

app_name = "mgmt"
urlpatterns = [
    url(r"^api/", include((router.urls, "api"))),
    # user task-list
    url(r"^my-assignments/$", views.UserAssignments.as_view(), name="user_assignments"),
    url(
        r"^my-assignments/(?P<pk>\d+)/$",
        views.UserAssessmentAssignments.as_view(),
        name="user_assessment_assignments",
    ),
    # assessment-level views
    url(r"^assessment/(?P<pk>\d+)/$", views.TaskDashboard.as_view(), name="assessment_dashboard",),
    url(r"^assessment/(?P<pk>\d+)/details/$", views.TaskDetail.as_view(), name="assessment_tasks",),
    url(r"^assessment/(?P<pk>\d+)/edit/$", views.TaskModify.as_view(), name="assessment_modify",),
]
