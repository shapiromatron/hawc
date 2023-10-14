from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"assessment", api.IVAssessmentViewSet, basename="assessment")
router.register(r"chemical", api.IVChemical, basename="chemical")
router.register(r"celltype", api.IVCellType, basename="celltype")
router.register(r"experiment", api.IVExperiment, basename="experiment")
router.register(r"endpoint", api.IVEndpoint, basename="endpoint")
router.register(r"category", api.IVEndpointCategory, basename="category")
router.register(r"ivendpoint-cleanup", api.IVEndpointCleanup, basename="ivendpoint-cleanup")
router.register(r"ivchemical-cleanup", api.IVChemicalCleanup, basename="ivchemical-cleanup")

app_name = "invitro"
urlpatterns = [
    # experiment
    path(
        "study/<int:pk>/create-experiment/",
        views.ExperimentCreate.as_view(),
        name="experiment_create",
    ),
    path(
        "experiment/<int:pk>/",
        views.ExperimentDetail.as_view(),
        name="experiment_detail",
    ),
    path(
        "experiment/<int:pk>/update/",
        views.ExperimentUpdate.as_view(),
        name="experiment_update",
    ),
    path(
        "experiment/<int:pk>/delete/",
        views.ExperimentDelete.as_view(),
        name="experiment_delete",
    ),
    # chemical
    path(
        "study/<int:pk>/create-chemical/",
        views.ChemicalCreate.as_view(),
        name="chemical_create",
    ),
    path(
        "chemical/<int:pk>/",
        views.ChemicalDetail.as_view(),
        name="chemical_detail",
    ),
    path(
        "chemical/<int:pk>/update/",
        views.ChemicalUpdate.as_view(),
        name="chemical_update",
    ),
    path(
        "chemical/<int:pk>/delete/",
        views.ChemicalDelete.as_view(),
        name="chemical_delete",
    ),
    # cell types
    path(
        "study/<int:pk>/create-cell-type/",
        views.CellTypeCreate.as_view(),
        name="celltype_create",
    ),
    path(
        "cell-type/<int:pk>/",
        views.CellTypeDetail.as_view(),
        name="celltype_detail",
    ),
    path(
        "cell-type/<int:pk>/update/",
        views.CellTypeUpdate.as_view(),
        name="celltype_update",
    ),
    path(
        "cell-type/<int:pk>/delete/",
        views.CellTypeDelete.as_view(),
        name="celltype_delete",
    ),
    # endpoint categories
    path(
        "assessment/<int:pk>/endpoint-categories/update/",
        views.EndpointCategoryUpdate.as_view(),
        name="endpointcategory_update",
    ),
    # endpoint
    path(
        "assessment/<int:pk>/endpoints/",
        views.EndpointFilterList.as_view(),
        name="endpoint_list",
    ),
    path(
        "experiment/<int:pk>/create-endpoint/",
        views.EndpointCreate.as_view(),
        name="endpoint_create",
    ),
    path(
        "endpoint/<int:pk>/",
        views.EndpointDetail.as_view(),
        name="endpoint_detail",
    ),
    path(
        "endpoint/<int:pk>/update/",
        views.EndpointUpdate.as_view(),
        name="endpoint_update",
    ),
    path(
        "endpoint/<int:pk>/delete/",
        views.EndpointDelete.as_view(),
        name="endpoint_delete",
    ),
    path("api/", include((router.urls, "api"))),
]
