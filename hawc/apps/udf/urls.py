from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register("assessment", api.UdfAssessmentViewSet, basename="assessment")

app_name = "udf"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    # UDF views
    path("", views.UDFListView.as_view(), name="udf_list"),
    path("create/", views.CreateUDFView.as_view(), name="udf_create"),
    path("<int:pk>/update/", views.UpdateUDFView.as_view(), name="udf_update"),
    path("<int:pk>/", views.UDFDetailView.as_view(), name="udf_detail"),
    path("preview/", views.SchemaPreview.as_view(), name="schema_preview"),
    # Model binding views
    path("assessment/<int:pk>/", views.UDFBindingList.as_view(), name="binding-list"),
    # binding objects
    path(
        "assessment/<int:pk>/bindings/<slug:binding_type>/create/",
        views.BindingViewSet.as_view(),
        {"action": "create"},
        name="binding_create",
    ),
    path(
        "bindings/<slug:binding_type>/<int:pk>/<slug:action>/",
        views.BindingViewSet.as_view(),
        name="binding_htmx",
    ),
]
