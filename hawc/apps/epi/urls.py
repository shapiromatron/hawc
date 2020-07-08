from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.EpiAssessmentViewset, basename="assessment")
router.register(r"study-population", api.StudyPopulation, basename="study-population")
router.register(r"exposure", api.Exposure, basename="exposure")
router.register(r"outcome", api.Outcome, basename="outcome")
router.register(r"result", api.Result, basename="result")
router.register(r"comparison-set", api.ComparisonSet, basename="set")
router.register(r"group", api.Group, basename="group")
router.register(r"outcome-cleanup", api.OutcomeCleanup, basename="outcome-cleanup")
router.register(
    r"studypopulation-cleanup", api.StudyPopulationCleanup, basename="studypopulation-cleanup",
)
router.register(r"exposure-cleanup", api.ExposureCleanup, basename="exposure-cleanup")


app_name = "epi"
urlpatterns = [
    url(r"^api/", include((router.urls, "api"))),
    # Heatmap views
    url(
        r"^assessment/(?P<pk>\d+)/heatmap-study-design/$",
        views.HeatmapStudyDesign.as_view(),
        name="heatmap_study_design",
    ),
    url(
        r"^assessment/(?P<pk>\d+)/heatmap-results/$",
        views.HeatmapResults.as_view(),
        name="heatmap_results",
    ),
    # Criteria
    url(
        r"^assessment/(?P<pk>\d+)/study-criteria/create/$",
        views.StudyCriteriaCreate.as_view(),
        name="studycriteria_create",
    ),
    # Adjustment factors
    url(
        r"^assessment/(?P<pk>\d+)/adjustment-factor/create/$",
        views.AdjustmentFactorCreate.as_view(),
        name="adjustmentfactor_create",
    ),
    # Study population
    url(
        r"^study/(?P<pk>\d+)/study-population/create/$",
        views.StudyPopulationCreate.as_view(),
        name="sp_create",
    ),
    url(
        r"^study/(?P<pk>\d+)/study-population/copy-as-new-selector/$",
        views.StudyPopulationCopyAsNewSelector.as_view(),
        name="sp_copy_selector",
    ),
    url(
        r"^study-population/(?P<pk>\d+)/$", views.StudyPopulationDetail.as_view(), name="sp_detail",
    ),
    url(
        r"^study-population/(?P<pk>\d+)/update/$",
        views.StudyPopulationUpdate.as_view(),
        name="sp_update",
    ),
    url(
        r"^study-population/(?P<pk>\d+)/delete/$",
        views.StudyPopulationDelete.as_view(),
        name="sp_delete",
    ),
    # Exposure
    url(
        r"^study/(?P<pk>\d+)/exposure/create/$", views.ExposureCreate.as_view(), name="exp_create",
    ),
    url(
        r"^study/(?P<pk>\d+)/exposure/copy-as-new-selector/$",
        views.ExposureCopyAsNewSelector.as_view(),
        name="exp_copy_selector",
    ),
    url(r"^exposure/(?P<pk>\d+)/$", views.ExposureDetail.as_view(), name="exp_detail"),
    url(r"^exposure/(?P<pk>\d+)/update/$", views.ExposureUpdate.as_view(), name="exp_update",),
    url(r"^exposure/(?P<pk>\d+)/delete/$", views.ExposureDelete.as_view(), name="exp_delete",),
    # Outcome
    url(r"^assessment/(?P<pk>\d+)/outcomes/$", views.OutcomeList.as_view(), name="outcome_list",),
    url(
        r"^study-population/(?P<pk>\d+)/outcome/create/$",
        views.OutcomeCreate.as_view(),
        name="outcome_create",
    ),
    url(
        r"^study-population/(?P<pk>\d+)/outcome/copy-as-new-selector/$",
        views.OutcomeCopyAsNewSelector.as_view(),
        name="outcome_copy_selector",
    ),
    url(r"^outcome/(?P<pk>\d+)/$", views.OutcomeDetail.as_view(), name="outcome_detail"),
    url(r"^outcome/(?P<pk>\d+)/update/$", views.OutcomeUpdate.as_view(), name="outcome_update",),
    url(r"^outcome/(?P<pk>\d+)/delete/$", views.OutcomeDelete.as_view(), name="outcome_delete",),
    # Results
    url(
        r"^outcome/(?P<pk>\d+)/result/create/$", views.ResultCreate.as_view(), name="result_create",
    ),
    url(
        r"^outcome/(?P<pk>\d+)/result/copy-as-new-selector/$",
        views.ResultCopyAsNewSelector.as_view(),
        name="result_copy_selector",
    ),
    url(r"^result/(?P<pk>\d+)/$", views.ResultDetail.as_view(), name="result_detail"),
    url(r"^result/(?P<pk>\d+)/update/$", views.ResultUpdate.as_view(), name="result_update",),
    url(r"^result/(?P<pk>\d+)/delete/$", views.ResultDelete.as_view(), name="result_delete",),
    # Comparison set
    url(
        r"^study-population/(?P<pk>\d+)/comparison-set/create/$",
        views.ComparisonSetCreate.as_view(),
        name="cs_create",
    ),
    url(
        r"^study-population/(?P<pk>\d+)/comparison-set/copy-as-new-selector/$",
        views.ComparisonSetStudyPopCopySelector.as_view(),
        name="cs_copy_selector",
    ),
    url(
        r"^outcome/(?P<pk>\d+)/comparison-set/create/$",
        views.ComparisonSetOutcomeCreate.as_view(),
        name="cs_outcome_create",
    ),
    url(
        r"^outcome/(?P<pk>\d+)/comparison-set/copy-as-new-selector/$",
        views.ComparisonSetOutcomeCopySelector.as_view(),
        name="cs_outcome_copy_selector",
    ),
    url(r"^comparison-set/(?P<pk>\d+)/$", views.ComparisonSetDetail.as_view(), name="cs_detail",),
    url(
        r"^comparison-set/(?P<pk>\d+)/update/$",
        views.ComparisonSetUpdate.as_view(),
        name="cs_update",
    ),
    url(
        r"^comparison-set/(?P<pk>\d+)/delete/$",
        views.ComparisonSetDelete.as_view(),
        name="cs_delete",
    ),
    # Groups (in comparison set)
    url(r"^group/(?P<pk>\d+)/$", views.GroupDetail.as_view(), name="g_detail"),
    url(r"^group/(?P<pk>\d+)/update/$", views.GroupUpdate.as_view(), name="g_update"),
]
