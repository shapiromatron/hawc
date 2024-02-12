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
            "bindings/<binding_type>/create/",
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
        path(
            "assessment/<int:pk>/create-model/",
            views.CreateModelBindingView.as_view(),
            name="model_create",
        ),
        path(
            "model/<int:pk>/update/",
            views.UpdateModelBindingView.as_view(),
            name="model_update",
        ),
        path("model/<int:pk>/", views.ModelBindingDetailView.as_view(), name="model_detail"),
        path("model/<int:pk>/delete/", views.DeleteModelBindingView.as_view(), name="model_delete"),
        # Tag binding views
        path(
            "assessment/<int:pk>/tag/create/",
            views.CreateTagBindingView.as_view(),
            name="tag_create",
        ),
        path(
            "tag/<int:pk>/update/",
            views.UpdateTagBindingView.as_view(),
            name="tag_update",
        ),
        path("tag/<int:pk>/", views.TagBindingDetailView.as_view(), name="tag_detail"),
        path("tag/<int:pk>/delete/", views.DeleteTagBindingView.as_view(), name="tag_delete"),
    ]
    if settings.HAWC_FEATURES.ENABLE_UDF
    else []
)
