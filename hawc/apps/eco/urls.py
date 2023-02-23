from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register("terms", api.TermViewSet, basename="terms")
router.register("assessment", api.AssessmentViewSet, basename="assessment")

app_name = "eco"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
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
    # cause
    path(
        "cause/<int:pk>/create/",
        views.CauseViewset.as_view(),
        {"action": "create"},
        name="cause-create",
    ),
    path(
        "cause/<int:pk>/",
        views.CauseViewset.as_view(),
        {"action": "read"},
        name="cause-detail",
    ),
    path(
        "cause/<int:pk>/clone/",
        views.CauseViewset.as_view(),
        {"action": "clone"},
        name="cause-clone",
    ),
    path(
        "cause/<int:pk>/update/",
        views.CauseViewset.as_view(),
        {"action": "update"},
        name="cause-update",
    ),
    path(
        "cause/<int:pk>/delete/",
        views.CauseViewset.as_view(),
        {"action": "delete"},
        name="cause-delete",
    ),
    # effect
    path(
        "effect/<int:pk>/create/",
        views.EffectViewset.as_view(),
        {"action": "create"},
        name="effect-create",
    ),
    path(
        "effect/<int:pk>/",
        views.EffectViewset.as_view(),
        {"action": "read"},
        name="effect-detail",
    ),
    path(
        "effect/<int:pk>/clone/",
        views.EffectViewset.as_view(),
        {"action": "clone"},
        name="effect-clone",
    ),
    path(
        "effect/<int:pk>/update/",
        views.EffectViewset.as_view(),
        {"action": "update"},
        name="effect-update",
    ),
    path(
        "effect/<int:pk>/delete/",
        views.EffectViewset.as_view(),
        {"action": "delete"},
        name="effect-delete",
    ),
    # result
    path(
        "result/<int:pk>/create/",
        views.ResultViewset.as_view(),
        {"action": "create"},
        name="result-create",
    ),
    path(
        "result/<int:pk>/",
        views.ResultViewset.as_view(),
        {"action": "read"},
        name="result-detail",
    ),
    path(
        "result/<int:pk>/clone/",
        views.ResultViewset.as_view(),
        {"action": "clone"},
        name="result-clone",
    ),
    path(
        "result/<int:pk>/update/",
        views.ResultViewset.as_view(),
        {"action": "update"},
        name="result-update",
    ),
    path(
        "result/<int:pk>/delete/",
        views.ResultViewset.as_view(),
        {"action": "delete"},
        name="result-delete",
    ),
]
