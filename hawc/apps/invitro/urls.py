from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.IVAssessmentViewset, basename="assessment")
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
    url(
        r"^study/(?P<pk>\d+)/create-experiment/$",
        views.ExperimentCreate.as_view(),
        name="experiment_create",
    ),
    url(r"^experiment/(?P<pk>\d+)/$", views.ExperimentDetail.as_view(), name="experiment_detail",),
    url(
        r"^experiment/(?P<pk>\d+)/update/$",
        views.ExperimentUpdate.as_view(),
        name="experiment_update",
    ),
    url(
        r"^experiment/(?P<pk>\d+)/delete/$",
        views.ExperimentDelete.as_view(),
        name="experiment_delete",
    ),
    # chemical
    url(
        r"^study/(?P<pk>\d+)/create-chemical/$",
        views.ChemicalCreate.as_view(),
        name="chemical_create",
    ),
    url(r"^chemical/(?P<pk>\d+)/$", views.ChemicalDetail.as_view(), name="chemical_detail",),
    url(r"^chemical/(?P<pk>\d+)/update/$", views.ChemicalUpdate.as_view(), name="chemical_update",),
    url(r"^chemical/(?P<pk>\d+)/delete/$", views.ChemicalDelete.as_view(), name="chemical_delete",),
    # cell types
    url(
        r"^study/(?P<pk>\d+)/create-cell-type/$",
        views.CellTypeCreate.as_view(),
        name="celltype_create",
    ),
    url(r"^cell-type/(?P<pk>\d+)/$", views.CellTypeDetail.as_view(), name="celltype_detail",),
    url(
        r"^cell-type/(?P<pk>\d+)/update/$", views.CellTypeUpdate.as_view(), name="celltype_update",
    ),
    url(
        r"^cell-type/(?P<pk>\d+)/delete/$", views.CellTypeDelete.as_view(), name="celltype_delete",
    ),
    # endpoint categories
    url(
        r"^assessment/(?P<pk>\d+)/endpoint-categories/update/$",
        views.EndpointCategoryUpdate.as_view(),
        name="endpointcategory_update",
    ),
    # endpoint
    url(
        r"^assessment/(?P<pk>\d+)/endpoints/$", views.EndpointList.as_view(), name="endpoint_list",
    ),
    url(
        r"^experiment/(?P<pk>\d+)/create-endpoint/$",
        views.EndpointCreate.as_view(),
        name="endpoint_create",
    ),
    url(r"^endpoint/(?P<pk>\d+)/$", views.EndpointDetail.as_view(), name="endpoint_detail",),
    url(r"^endpoint/(?P<pk>\d+)/update/$", views.EndpointUpdate.as_view(), name="endpoint_update",),
    url(r"^endpoint/(?P<pk>\d+)/delete/$", views.EndpointDelete.as_view(), name="endpoint_delete",),
    url(r"^api/", include((router.urls, "api"))),
]
