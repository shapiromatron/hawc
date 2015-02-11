from django.conf.urls import patterns, url, include

from rest_framework.routers import DefaultRouter

from . import views, api


router = DefaultRouter()
router.register(r'endpoint', api.Endpoint, base_name="endpoint")


urlpatterns = patterns('animal.views',

    # Overall views
    url(r'^assessment/(?P<pk>\d+)/full-export/$', views.FullExport.as_view(), name='export'),
    url(r'^assessment/(?P<pk>\d+)/report/$', views.EndpointsReport.as_view(), name='endpoints_report'),
    url(r'^assessment/(?P<pk>\d+)/fixed-report/$', views.EndpointsFixedReport.as_view(), name='endpoints_fixedreport'),

    # Experiment
    url(r'^study/(?P<pk>\d+)/experiment/new/$', views.ExperimentCreate.as_view(), name='experiment_new'),
    url(r'^experiment/(?P<pk>\d+)/$', views.ExperimentRead.as_view(), name='experiment_detail'),
    url(r'^experiment/(?P<pk>\d+)/edit/$', views.ExperimentUpdate.as_view(), name='experiment_update'),
    url(r'^experiment/(?P<pk>\d+)/delete/$', views.ExperimentDelete.as_view(), name='experiment_delete'),

    # AnimalGroup
    url(r'^experiment/(?P<pk>\d+)/animal-group/new/$', views.AnimalGroupCreate.as_view(), name='animal_group_new'),
    url(r'^animal-group/(?P<pk>\d+)/$', views.AnimalGroupRead.as_view(), name='animal_group_detail'),
    url(r'^animal-group/(?P<pk>\d+)/edit/$', views.AnimalGroupUpdate.as_view(), name='animal_group_update'),
    url(r'^animal-group/(?P<pk>\d+)/delete/$', views.AnimalGroupDelete.as_view(), name='animal_group_delete'),
    url(r'^animal-group/(?P<pk>\d+)/endpoint/copy-as-new-selector/$', views.EndpointCopyAsNewSelector.as_view(), name='endpoint_copy_selector'),

    # Dosing Regime
    url(r'^dosing-regime/(?P<pk>\d+)/edit/$', views.DosingRegimeUpdate.as_view(), name='dosing_regime_update'),

    # Endpoint
    url(r'^assessment/(?P<pk>\d+)/endpoints/$', views.EndpointList.as_view(), name='endpoint_list'),
    url(r'^assessment/(?P<pk>\d+)/endpoints/tags/(?P<tag_slug>[-\w]+)/$', views.EndpointTags.as_view(), name='assessment_endpoint_taglist'),
    url(r'^assessment/(?P<pk>\d+)/endpoints/search/$', views.EndpointSearch.as_view(), name='assessment_endpoint_search'),
    url(r'^animal-group/(?P<pk>\d+)/endpoint/new/$', views.EndpointCreate.as_view(), name='endpoint_new'),
    url(r'^animal-group/(?P<pk>\d+)/endpoint/individual-animal-data/new/$', views.EndpointIndividualAnimalCreate.as_view(), name='endpoint_individual_animal_new'),
    url(r'^endpoint/(?P<pk>\d+)/$', views.EndpointRead.as_view(), name='endpoint_detail'),
    url(r'^endpoint/(?P<pk>\d+)/json/', views.EndpointReadJSON.as_view(), name='endpoint_json'),
    url(r'^endpoint/(?P<pk>\d+)/dose-response-plot/$', views.EndpointDRplot.as_view(), name='endpoint_dr'),
    url(r'^endpoint/(?P<pk>\d+)/edit/$', views.EndpointUpdate.as_view(), name='endpoint_update'),
    url(r'^endpoint/(?P<pk>\d+)/individual-animal-data/edit/$', views.EndpointIndividualAnimalUpdate.as_view(), name='endpoint_individual_animal_update'),
    url(r'^endpoint/(?P<pk>\d+)/delete/$', views.EndpointDelete.as_view(), name='endpoint_delete'),
    url(r'^assessment/(?P<pk>\d+)/endpoints/flatfile/$', views.EndpointFlatFile.as_view(), name='endpoints_flatfile'),
    url(r'^assessment/(?P<pk>\d+)/endpoints/crossview/$', views.EndpointCrossview.as_view(), name='endpoint_crossview'),

    # Endpoint-level uncertainty factor
    url(r'^endpoint/(?P<pk>\d+)/ufs/$', views.UFList.as_view(), name='ufs_list'),
    url(r'^endpoint/(?P<pk>\d+)/uf/create/$', views.UFCreate.as_view(), name='uf_create'),
    url(r'^endpoint/uf/(?P<pk>\d+)/$', views.UFRead.as_view(), name='uf_detail'),
    url(r'^endpoint/uf/(?P<pk>\d+)/edit/$', views.UFEdit.as_view(), name='uf_edit'),
    url(r'^endpoint/uf/(?P<pk>\d+)/delete/$', views.UFDelete.as_view(), name='uf_delete'),

    # Aggregation-level uncertainty views
    url(r'^aggregation/(?P<pk>\d+)/ufs/edit/$', views.UFsAggEdit.as_view(), name='ufs_agg_edit'),
    url(r'^aggregation/(?P<pk>\d+)/ufs/$', views.UFsAggRead.as_view(), name='ufs_agg_read'),

    # Aggregations
    url(r'^(?P<pk>\d+)/aggregation/$', views.AggregationAssessmentList.as_view(), name='aggregation_list'),
    url(r'^(?P<pk>\d+)/aggregation/new/$', views.AggregationCreate.as_view(), name='aggregation_new'),
    url(r'^(?P<pk>\d+)/aggregation/search/$', views.AggregationSearch.as_view(), name='aggregation_search'),
    url(r'^aggregation/(?P<pk>\d+)/edit/$', views.AggregationUpdate.as_view(), name='aggregation_update'),
    url(r'^aggregation/(?P<pk>\d+)/delete/$', views.AggregationDelete.as_view(), name='aggregation_delete'),
    url(r'^aggregation/(?P<pk>\d+)/versions/$', views.AggregationVersions.as_view(), name='aggregation_versions'),
    url(r'^aggregation/(?P<pk>\d+)/$', views.AggregationRead.as_view(), name='aggregation_detail'),
    url(r'^aggregation/(?P<pk>\d+)/json/$', views.AggregationReadJSON.as_view(), name='aggregation_json'),
    url(r'^assessment/(?P<pk>\d+)/aggregation-endpoint-filter/$', views.AggregationEndpointFilter.as_view(), name='aggregation_endpoint_filter'),

    # Reference Values
    url(r'^assessment/(?P<pk>\d+)/reference-value/create/$', views.RefValCreate.as_view(), name='ref_val_create'),
    url(r'^assessment/(?P<pk>\d+)/reference-values/$', views.RefValList.as_view(), name='ref_val_list'),
    url(r'^reference-value/(?P<pk>\d+)/$', views.RefValRead.as_view(), name='ref_val'),
    url(r'^reference-value/(?P<pk>\d+)/edit/$', views.RefValUpdate.as_view(), name='ref_val_update'),
    url(r'^reference-value/(?P<pk>\d+)/delete/$', views.RefValDelete.as_view(), name='ref_val_delete'),

    # (Other)
    url(r'^aggregation/review-plot/$', views.ReviewPlot.as_view(), name='review_plot'),
    url(r'^endpoint/time-dose-response-plot/$', views.EndpointTDRplot.as_view(), name='time_endpoint_dr'),
    url(r'^strains/', views.getStrains.as_view(), name='get_strains'),
    url(r'^assessment/(?P<pk>\d+)/species/create/$', views.SpeciesCreate.as_view(), name='species_create'),
    url(r'^assessment/(?P<pk>\d+)/strain/create/$', views.StrainCreate.as_view(), name='strain_create'),
    url(r'^assessment/(?P<pk>\d+)/dose-units/create/$', views.DoseUnitsCreate.as_view(), name='dose_units_create'),

    url(r'^api/', include(router.urls))
)
