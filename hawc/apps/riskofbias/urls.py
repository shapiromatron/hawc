from django.urls import include, path
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
    path("api/", include((router.urls, "api"))),
    # modify assessment rob settings
    path("assessment/<int:pk>/", views.ARoBDetail.as_view(), name="arob_detail"),
    path("assessment/<int:pk>/copy/", views.ARoBCopy.as_view(), name="arob_copy"),
    path("assessment/<int:pk>/update/", views.ARoBEdit.as_view(), name="arob_update"),
    path(
        "assessment/<int:pk>/text-update/", views.ARoBTextEdit.as_view(), name="arob_text_update",
    ),
    # modify domains
    path(
        "assessment/<int:pk>/domain/create/", views.RoBDomainCreate.as_view(), name="robd_create",
    ),
    path("domain/<int:pk>/update/", views.RoBDomainUpdate.as_view(), name="robd_update",),
    path("domain/<int:pk>/delete/", views.RoBDomainDelete.as_view(), name="robd_delete",),
    # modify metrics
    path("domain/<int:pk>/metric/create/", views.RoBMetricCreate.as_view(), name="robm_create",),
    path("metric/<int:pk>/update/", views.RoBMetricUpdate.as_view(), name="robm_update",),
    path("metric/<int:pk>/delete/", views.RoBMetricDelete.as_view(), name="robm_delete",),
    # rob reviewers
    path(
        "assessment/<int:pk>/study-assignments/",
        views.ARoBReviewersList.as_view(),
        name="arob_reviewers",
    ),
    path(
        "assessment/<int:pk>/study-assignments/update/",
        views.ARoBReviewersUpdate.as_view(),
        name="arob_reviewers_update",
    ),
    # rob at study-level
    path("study/<int:pk>/", views.RoBDetail.as_view(), name="rob_detail"),
    path("study/<int:pk>/all/", views.RoBsDetailAll.as_view(), name="rob_detail_all",),
    # rob editing views
    path("<int:pk>/update/", views.RoBEdit.as_view(), name="rob_update"),
]
