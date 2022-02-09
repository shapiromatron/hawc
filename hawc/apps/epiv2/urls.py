from django.urls import path

from . import views

app_name = "epiv2"
urlpatterns = [
    path("study/<int:pk>/design/create/", views.DesignCreate.as_view(), name="design_create",),
    path("design/<int:pk>/update/", views.DesignUpdate.as_view(), name="design_update",),
    path("design/<int:pk>/", views.DesignDetail.as_view(), name="design_detail",),
    path("design/<int:pk>/delete/", views.DesignDelete.as_view(), name="design_delete",),
    # design htmx viewset
    path(
        "designv2/<int:pk>/create/",
        views.DesignViewset.as_view(),
        {"action": "create"},
        name="design-create",
    ),
    path(
        "designv2/<int:pk>/",
        views.DesignViewset.as_view(),
        {"action": "read"},
        name="design-detail",
    ),
    path(
        "designv2/<int:pk>/clone/",
        views.DesignViewset.as_view(),
        {"action": "clone"},
        name="design-clone",
    ),
    path(
        "designv2/<int:pk>/update/",
        views.DesignViewset.as_view(),
        {"action": "update"},
        name="design-update",
    ),
    path(
        "designv2/<int:pk>/delete/",
        views.DesignViewset.as_view(),
        {"action": "delete"},
        name="design-delete",
    ),
    # criteria
    path(
        "criteria/<int:pk>/create/",
        views.CriteriaViewset.as_view(),
        {"action": "create"},
        name="criteria-create",
    ),
    path(
        "chemical/<int:pk>/",
        views.CriteriaViewset.as_view(),
        {"action": "read"},
        name="criteria-detail",
    ),
    path(
        "chemical/<int:pk>/clone/",
        views.CriteriaViewset.as_view(),
        {"action": "clone"},
        name="criteria-clone",
    ),
    path(
        "chemical/<int:pk>/update/",
        views.CriteriaViewset.as_view(),
        {"action": "update"},
        name="criteria-update",
    ),
    path(
        "chemical/<int:pk>/delete/",
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
]
