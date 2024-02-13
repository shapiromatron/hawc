from django.conf import settings
from django.urls import path

from . import views

app_name = "udf"
urlpatterns = (
    [
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
            "assessment/<int:pk>/bindings/<binding_type>/create/",
            views.BindingViewSet.as_view(),
            {"action": "create"},
            name="binding_create",
        ),
        path(
            "bindings/<binding_type>/<int:pk>/",
            views.BindingViewSet.as_view(),
            {"action": "read"},
            name="binding_detail",
        ),
        path(
            "bindings/<binding_type>/<int:pk>/update/",
            views.BindingViewSet.as_view(),
            {"action": "update"},
            name="binding_update",
        ),
        path(
            "bindings/<binding_type>/<int:pk>/delete/",
            views.BindingViewSet.as_view(),
            {"action": "delete"},
            name="binding_delete",
        ),
    ]
    if settings.HAWC_FEATURES.ENABLE_UDF
    else []
)
