from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"assessment", api.EpiAssessmentViewSet, basename="assessment")
router.register(r"study-population", api.StudyPopulation, basename="study-population")
router.register(r"criteria", api.Criteria, basename="criteria")
router.register(r"exposure", api.Exposure, basename="exposure")
router.register(r"outcome", api.Outcome, basename="outcome")
router.register(r"result", api.Result, basename="result")
router.register(r"comparison-set", api.ComparisonSet, basename="set")
router.register(r"group", api.Group, basename="group")
router.register(r"group-result", api.GroupResult, basename="group-result")
router.register(
    r"numerical-descriptions", api.GroupNumericalDescriptions, basename="numerical-descriptions"
)
router.register(r"outcome-cleanup", api.OutcomeCleanup, basename="outcome-cleanup")
router.register(
    r"studypopulation-cleanup",
    api.StudyPopulationCleanup,
    basename="studypopulation-cleanup",
)
router.register(r"exposure-cleanup", api.ExposureCleanup, basename="exposure-cleanup")
router.register(r"metadata", api.Metadata, basename="metadata")


app_name = "epi"
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
    # Criteria
    path(
        "assessment/<int:pk>/study-criteria/create/",
        views.StudyCriteriaCreate.as_view(),
        name="studycriteria_create",
    ),
    # Adjustment factors
    path(
        "assessment/<int:pk>/adjustment-factor/create/",
        views.AdjustmentFactorCreate.as_view(),
        name="adjustmentfactor_create",
    ),
    # Study population
    path(
        "study/<int:pk>/study-population/create/",
        views.StudyPopulationCreate.as_view(),
        name="sp_create",
    ),
    path(
        "study/<int:pk>/study-population/copy-as-new-selector/",
        views.StudyPopulationCopyAsNewSelector.as_view(),
        name="sp_copy_selector",
    ),
    path(
        "study-population/<int:pk>/",
        views.StudyPopulationDetail.as_view(),
        name="sp_detail",
    ),
    path(
        "study-population/<int:pk>/update/",
        views.StudyPopulationUpdate.as_view(),
        name="sp_update",
    ),
    path(
        "study-population/<int:pk>/delete/",
        views.StudyPopulationDelete.as_view(),
        name="sp_delete",
    ),
    # Exposure
    path(
        "study/<int:pk>/exposure/create/",
        views.ExposureCreate.as_view(),
        name="exp_create",
    ),
    path(
        "study/<int:pk>/exposure/copy-as-new-selector/",
        views.ExposureCopyAsNewSelector.as_view(),
        name="exp_copy_selector",
    ),
    path("exposure/<int:pk>/", views.ExposureDetail.as_view(), name="exp_detail"),
    path(
        "exposure/<int:pk>/update/",
        views.ExposureUpdate.as_view(),
        name="exp_update",
    ),
    path(
        "exposure/<int:pk>/delete/",
        views.ExposureDelete.as_view(),
        name="exp_delete",
    ),
    # Outcome
    path(
        "assessment/<int:pk>/outcomes/",
        views.OutcomeFilterList.as_view(),
        name="outcome_list",
    ),
    path(
        "study-population/<int:pk>/outcome/create/",
        views.OutcomeCreate.as_view(),
        name="outcome_create",
    ),
    path(
        "study-population/<int:pk>/outcome/copy-as-new-selector/",
        views.OutcomeCopyAsNewSelector.as_view(),
        name="outcome_copy_selector",
    ),
    path("outcome/<int:pk>/", views.OutcomeDetail.as_view(), name="outcome_detail"),
    path(
        "outcome/<int:pk>/update/",
        views.OutcomeUpdate.as_view(),
        name="outcome_update",
    ),
    path(
        "outcome/<int:pk>/delete/",
        views.OutcomeDelete.as_view(),
        name="outcome_delete",
    ),
    # Results
    path(
        "outcome/<int:pk>/result/create/",
        views.ResultCreate.as_view(),
        name="result_create",
    ),
    path(
        "outcome/<int:pk>/result/copy-as-new-selector/",
        views.ResultCopyAsNewSelector.as_view(),
        name="result_copy_selector",
    ),
    path("result/<int:pk>/", views.ResultDetail.as_view(), name="result_detail"),
    path(
        "result/<int:pk>/update/",
        views.ResultUpdate.as_view(),
        name="result_update",
    ),
    path(
        "result/<int:pk>/delete/",
        views.ResultDelete.as_view(),
        name="result_delete",
    ),
    # Comparison set
    path(
        "study-population/<int:pk>/comparison-set/create/",
        views.ComparisonSetCreate.as_view(),
        name="cs_create",
    ),
    path(
        "study-population/<int:pk>/comparison-set/copy-as-new-selector/",
        views.ComparisonSetStudyPopCopySelector.as_view(),
        name="cs_copy_selector",
    ),
    path(
        "outcome/<int:pk>/comparison-set/create/",
        views.ComparisonSetOutcomeCreate.as_view(),
        name="cs_outcome_create",
    ),
    path(
        "outcome/<int:pk>/comparison-set/copy-as-new-selector/",
        views.ComparisonSetOutcomeCopySelector.as_view(),
        name="cs_outcome_copy_selector",
    ),
    path(
        "comparison-set/<int:pk>/",
        views.ComparisonSetDetail.as_view(),
        name="cs_detail",
    ),
    path(
        "comparison-set/<int:pk>/update/",
        views.ComparisonSetUpdate.as_view(),
        name="cs_update",
    ),
    path(
        "comparison-set/<int:pk>/delete/",
        views.ComparisonSetDelete.as_view(),
        name="cs_delete",
    ),
    # Groups (in comparison set)
    path("group/<int:pk>/", views.GroupDetail.as_view(), name="g_detail"),
    path("group/<int:pk>/update/", views.GroupUpdate.as_view(), name="g_update"),
]
