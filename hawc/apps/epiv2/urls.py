from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"design", api.Design, basename="design")

app_name = "epiv2"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    path("study/<int:pk>/design/create/", views.DesignCreate.as_view(), name="design_create",),
    path("design/<int:pk>/update/", views.DesignUpdate.as_view(), name="design_update",),
    path("design/<int:pk>/", views.DesignDetail.as_view(), name="design_detail",),
    path("design/<int:pk>/delete/", views.DesignDelete.as_view(), name="design_delete",),
    # design htmx viewset
    path(
        "designv2/<int:pk>/",
        views.DesignViewset.as_view(),
        {"action": "read"},
        name="design-detail",
    ),
    path(
        "designv2/<int:pk>/update/",
        views.DesignViewset.as_view(),
        {"action": "update"},
        name="design-update",
    ),
    # criteria
    path(
        "criteria/<int:pk>/create/",
        views.CriteriaViewset.as_view(),
        {"action": "create"},
        name="criteria-create",
    ),
    path(
        "criteria/<int:pk>/",
        views.CriteriaViewset.as_view(),
        {"action": "read"},
        name="criteria-detail",
    ),
    path(
        "criteria/<int:pk>/clone/",
        views.CriteriaViewset.as_view(),
        {"action": "clone"},
        name="criteria-clone",
    ),
    path(
        "criteria/<int:pk>/update/",
        views.CriteriaViewset.as_view(),
        {"action": "update"},
        name="criteria-update",
    ),
    path(
        "criteria/<int:pk>/delete/",
        views.CriteriaViewset.as_view(),
        {"action": "delete"},
        name="criteria-delete",
    ),
    # chemical
    path(
        "chemical/<int:pk>/create/",
        views.ChemicalViewset.as_view(),
        {"action": "create"},
        name="chemical-create",
    ),
    path(
        "chemical/<int:pk>/",
        views.ChemicalViewset.as_view(),
        {"action": "read"},
        name="chemical-detail",
    ),
    path(
        "chemical/<int:pk>/clone/",
        views.ChemicalViewset.as_view(),
        {"action": "clone"},
        name="chemical-clone",
    ),
    path(
        "chemical/<int:pk>/update/",
        views.ChemicalViewset.as_view(),
        {"action": "update"},
        name="chemical-update",
    ),
    path(
        "chemical/<int:pk>/delete/",
        views.ChemicalViewset.as_view(),
        {"action": "delete"},
        name="chemical-delete",
    ),
    # exposure
    path(
        "exposure/<int:pk>/create/",
        views.ExposureViewset.as_view(),
        {"action": "create"},
        name="exposure-create",
    ),
    path(
        "exposure/<int:pk>/",
        views.ExposureViewset.as_view(),
        {"action": "read"},
        name="exposure-detail",
    ),
    path(
        "exposure/<int:pk>/clone/",
        views.ExposureViewset.as_view(),
        {"action": "clone"},
        name="exposure-clone",
    ),
    path(
        "exposure/<int:pk>/update/",
        views.ExposureViewset.as_view(),
        {"action": "update"},
        name="exposure-update",
    ),
    path(
        "exposure/<int:pk>/delete/",
        views.ExposureViewset.as_view(),
        {"action": "delete"},
        name="exposure-delete",
    ),
    # exposure level
    path(
        "exposurelevel/<int:pk>/create/",
        views.ExposureLevelViewset.as_view(),
        {"action": "create"},
        name="exposurelevel-create",
    ),
    path(
        "exposurelevel/<int:pk>/",
        views.ExposureLevelViewset.as_view(),
        {"action": "read"},
        name="exposurelevel-detail",
    ),
    path(
        "exposurelevel/<int:pk>/clone/",
        views.ExposureLevelViewset.as_view(),
        {"action": "clone"},
        name="exposurelevel-clone",
    ),
    path(
        "exposurelevel/<int:pk>/update/",
        views.ExposureLevelViewset.as_view(),
        {"action": "update"},
        name="exposurelevel-update",
    ),
    path(
        "exposurelevel/<int:pk>/delete/",
        views.ExposureLevelViewset.as_view(),
        {"action": "delete"},
        name="exposurelevel-delete",
    ),
    # outcome
    path(
        "outcome/<int:pk>/create/",
        views.OutcomeViewset.as_view(),
        {"action": "create"},
        name="outcome-create",
    ),
    path(
        "outcome/<int:pk>/",
        views.OutcomeViewset.as_view(),
        {"action": "read"},
        name="outcome-detail",
    ),
    path(
        "outcome/<int:pk>/clone/",
        views.OutcomeViewset.as_view(),
        {"action": "clone"},
        name="outcome-clone",
    ),
    path(
        "outcome/<int:pk>/update/",
        views.OutcomeViewset.as_view(),
        {"action": "update"},
        name="outcome-update",
    ),
    path(
        "outcome/<int:pk>/delete/",
        views.OutcomeViewset.as_view(),
        {"action": "delete"},
        name="outcome-delete",
    ),
    # adjustment factor
    path(
        "adjustmentfactor/<int:pk>/create/",
        views.AdjustmentFactorViewset.as_view(),
        {"action": "create"},
        name="adjustmentfactor-create",
    ),
    path(
        "adjustmentfactor/<int:pk>/",
        views.AdjustmentFactorViewset.as_view(),
        {"action": "read"},
        name="adjustmentfactor-detail",
    ),
    path(
        "adjustmentfactor/<int:pk>/clone/",
        views.AdjustmentFactorViewset.as_view(),
        {"action": "clone"},
        name="adjustmentfactor-clone",
    ),
    path(
        "adjustmentfactor/<int:pk>/update/",
        views.AdjustmentFactorViewset.as_view(),
        {"action": "update"},
        name="adjustmentfactor-update",
    ),
    path(
        "adjustmentfactor/<int:pk>/delete/",
        views.AdjustmentFactorViewset.as_view(),
        {"action": "delete"},
        name="adjustmentfactor-delete",
    ),
    # data extraction
    path(
        "dataextraction/<int:pk>/create/",
        views.DataExtractionViewset.as_view(),
        {"action": "create"},
        name="dataextraction-create",
    ),
    path(
        "dataextraction/<int:pk>/",
        views.DataExtractionViewset.as_view(),
        {"action": "read"},
        name="dataextraction-detail",
    ),
    path(
        "dataextraction/<int:pk>/clone/",
        views.DataExtractionViewset.as_view(),
        {"action": "clone"},
        name="dataextraction-clone",
    ),
    path(
        "dataextraction/<int:pk>/update/",
        views.DataExtractionViewset.as_view(),
        {"action": "update"},
        name="dataextraction-update",
    ),
    path(
        "dataextraction/<int:pk>/delete/",
        views.DataExtractionViewset.as_view(),
        {"action": "delete"},
        name="dataextraction-delete",
    ),
]
