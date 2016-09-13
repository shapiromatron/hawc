from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import api, views


router = DefaultRouter()
router.register(r'task', api.Task, base_name="task")


urlpatterns = [

    url(r'^api/', include(router.urls, namespace='api')),

    # user task-list
    url(r'^my-assignments/$',
        views.UserAssignments.as_view(),
        name='user_assignments'),

    # assessment-level views
    url(r'^assessment/(?P<pk>\d+)/$',
        views.TaskDashboard.as_view(),
        name='assessment_dashboard'),
    url(r'^assessment/(?P<pk>\d+)/details/$',
        views.TaskDetail.as_view(),
        name='assessment_tasks'),
    url(r'^assessment/(?P<pk>\d+)/edit/$',
        views.TaskModify.as_view(),
        name='assessment_modify'),
]
