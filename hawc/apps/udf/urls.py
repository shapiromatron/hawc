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
        path("binding/create/", views.CreateModelBindingView.as_view(), name="binding_create"),
        # path(
        #     "binding/<int:pk>/update/",
        #     views.UpdateModelBindingView.as_view(),
        #     name="binding_update",
        # ),
        # path("binding/<int:pk>/", views.ModelBindingDetailView.as_view(), name="binding_detail"),
        # # Tag binding views
        # path("tag-binding/create/", views.CreateTagBindingView.as_view(), name="binding_create"),
        # path(
        #     "tag-binding/<int:pk>/update/",
        #     views.UpdateTagBindingView.as_view(),
        #     name="binding_update",
        # ),
        # path("tag-binding/<int:pk>/", views.TagBindingDetailView.as_view(), name="binding_detail"),
    ]
    if settings.HAWC_FEATURES.ENABLE_UDF
    else []
)
