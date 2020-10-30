from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.RiskOfBiasAssessmentViewset, basename="assessment")
router.register(r"domain", api.RiskOfBiasDomain, basename="domain")
router.register(r"review", api.RiskOfBias, basename="review")
router.register(r"metrics", api.AssessmentMetricViewset, basename="metrics")
router.register(r"metrics/scores", api.AssessmentMetricScoreViewset, basename="metric_scores")
router.register(r"scores", api.AssessmentScoreViewset, basename="scores")
router.register(r"score-cleanup", api.ScoreCleanupViewset, basename="score-cleanup")

app_name = "riskofbias"
urlpatterns = [
    re_path(r"^api/", include((router.urls, "api"))),
    # modify assessment rob settings
    re_path(r"^assessment/(?P<pk>\d+)/$", views.ARoBDetail.as_view(), name="arob_detail"),
    re_path(r"^assessment/(?P<pk>\d+)/copy/$", views.ARoBCopy.as_view(), name="arob_copy"),
    re_path(r"^assessment/(?P<pk>\d+)/edit/$", views.ARoBEdit.as_view(), name="arob_update"),
    re_path(
        r"^assessment/(?P<pk>\d+)/text-edit/$",
        views.ARoBTextEdit.as_view(),
        name="arob_text_update",
    ),
    # modify domains
    re_path(
        r"^assessment/(?P<pk>\d+)/domain/create/$",
        views.RoBDomainCreate.as_view(),
        name="robd_create",
    ),
    re_path(r"^domain/(?P<pk>\d+)/edit/$", views.RoBDomainUpdate.as_view(), name="robd_update",),
    re_path(r"^domain/(?P<pk>\d+)/delete/$", views.RoBDomainDelete.as_view(), name="robd_delete",),
    # modify metrics
    re_path(
        r"^domain/(?P<pk>\d+)/metric/create/$", views.RoBMetricCreate.as_view(), name="robm_create",
    ),
    re_path(r"^metric/(?P<pk>\d+)/edit/$", views.RoBMetricUpdate.as_view(), name="robm_update",),
    re_path(r"^metric/(?P<pk>\d+)/delete/$", views.RoBMetricDelete.as_view(), name="robm_delete",),
    # rob reviewers
    re_path(
        r"^assessment/(?P<pk>\d+)/study-assignments/$",
        views.ARoBReviewersList.as_view(),
        name="arob_reviewers",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/study-assignments/edit/$",
        views.ARoBReviewersUpdate.as_view(),
        name="arob_reviewers_update",
    ),
    # rob at study-level
    re_path(r"^study/(?P<pk>\d+)/$", views.RoBDetail.as_view(), name="rob_detail"),
    re_path(r"^study/(?P<pk>\d+)/all/$", views.RoBsDetailAll.as_view(), name="rob_detail_all",),
    # rob editing views
    re_path(r"^(?P<pk>\d+)/edit/$", views.RoBEdit.as_view(), name="rob_update"),
]
