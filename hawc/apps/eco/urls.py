from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register("terms", api.TermViewSet, basename="terms")
router.register("assessment", api.AssessmentViewSet, basename="assessment")
router.register("design-cleanup", api.DesignCleanupViewSet, basename="design-cleanup")
router.register("cause-cleanup", api.CauseCleanupViewSet, basename="cause-cleanup")
router.register("effect-cleanup", api.EffectCleanupViewSet, basename="effect-cleanup")
router.register("result-cleanup", api.ResultCleanupViewSet, basename="result-cleanup")

app_name = "eco"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    # Heatmap views
    path(
        "assessment/<int:pk>/heatmap-study-design/",
        views.HeatmapStudyDesign.as_view(),
        name="heatmap_study_design",
    ),
    path(
        "assessment/<int:pk>/heatmap-results/",
        views.HeatmapResults.as_view(),
        name="heatmap_results",
    ),
    path("terms/", views.NestedTermList.as_view(), name="term_list"),
    path(
        "study/<int:pk>/design/create/",
        views.DesignCreate.as_view(),
        name="design_create",
    ),
    path(
        "design/<int:pk>/update/",
        views.DesignUpdate.as_view(),
        name="design_update",
    ),
    path(
        "design/<int:pk>/",
        views.DesignDetail.as_view(),
        name="design_detail",
    ),
    path(
        "design/<int:pk>/delete/",
        views.DesignDelete.as_view(),
        name="design_delete",
    ),
    path(
        "designv2/<int:pk>/<slug:action>/",
        views.DesignViewSet.as_view(),
        name="design-htmx",
    ),
    # cause
    path(
        "cause/<int:pk>/<slug:action>/",
        views.CauseViewSet.as_view(),
        name="cause-htmx",
    ),
    # effect
    path(
        "effect/<int:pk>/<slug:action>/",
        views.EffectViewSet.as_view(),
        name="effect-htmx",
    ),
    # result
    path(
        "result/<int:pk>/<slug:action>/",
        views.ResultViewSet.as_view(),
        name="result-htmx",
    ),
    path(
        "assessment/<int:pk>/results/",
        views.ResultFilterList.as_view(),
        name="result_list",
    ),
]
