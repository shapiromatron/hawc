from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views, api

router = DefaultRouter()
router.register(r'meta-result', api.MetaResult, base_name="meta-result")
router.register(r'study-population', api.StudyPopulation, base_name="study-population")
router.register(r'exposure', api.Exposure, base_name="exposure")
router.register(r'assessed-outcome', api.AssessedOutcome, base_name="assessed-outcome")

urlpatterns = [

    # overall views
    url(r'^assessment/(?P<pk>\d+)/full-export/$',
        views.FullExport.as_view(),
        name='export'),

    url(r'^assessment/(?P<pk>\d+)/assessed-outcomes/$',
        views.AssessedOutcomeList.as_view(),
        name='assessedoutcome_list'),

    url(r'^assessment/(?P<pk>\d+)/report/$',
        views.AssessedOutcomeReport.as_view(),
        name='ao_report'),

    url(r'^assessment/(?P<pk>\d+)/meta-result-report/$',
        views.MetaResultReport.as_view(),
        name='mr_report'),

    url(r'^assessment/(?P<pk>\d+)/meta-result-full-export/$',
        views.MetaResultFullExport.as_view(),
        name='mr_export'),

    # study-criteria views
    url(r'^assessment/(?P<pk>\d+)/study-criteria/create/$',
        views.StudyCriteriaCreate.as_view(),
        name='studycriteria_create'),

    # study-population views
    url(r'^study/(?P<pk>\d+)/study-population/create/$',
        views.StudyPopulationCreate.as_view(),
        name='sp_create'),

    url(r'^study/(?P<pk>\d+)/study-population/copy-as-new-selector/$',
        views.StudyPopulationCopyAsNewSelector.as_view(),
        name='sp_copy_selector'),

    url(r'^study-population/(?P<pk>\d+)/$',
        views.StudyPopulationDetail.as_view(),
        name='sp_detail'),

    url(r'^study-population/(?P<pk>\d+)/update/$',
        views.StudyPopulationUpdate.as_view(),
        name='sp_update'),

    url(r'^study-population/(?P<pk>\d+)/delete/$',
        views.StudyPopulationDelete.as_view(),
        name='sp_delete'),

    # exposure views
    url(r'^study-population/(?P<pk>\d+)/exposure/create/$',
        views.ExposureCreate.as_view(),
        name='exposure_create'),

    url(r'^study-population/(?P<pk>\d+)/exposure/copy-as-new-selector/$',
        views.ExposureCopyAsNewSelector.as_view(),
        name='exposure_copy_selector'),

    url(r'^exposure/(?P<pk>\d+)/$',
        views.ExposureDetail.as_view(),
        name='exposure_detail'),

    url(r'^exposure/(?P<pk>\d+)/update/$',
        views.ExposureUpdate.as_view(),
        name='exposure_update'),

    url(r'^exposure/(?P<pk>\d+)/delete/$',
        views.ExposureDelete.as_view(),
        name='exposure_delete'),

    # factor views
    url(r'^assessment/(?P<pk>\d+)/factors/create/$',
        views.FactorCreate.as_view(),
        name='factor_create'),

    # assessed-outcome views
    url(r'^exposure/(?P<pk>\d+)/assessed-outcome/create/$',
        views.AssessedOutcomeCreate.as_view(),
        name='assessedoutcome_create'),

    url(r'^exposure/(?P<pk>\d+)/assessed-outcome/copy-as-new-selector/$',
        views.AssessedOutcomeCopyAsNewSelector.as_view(),
        name='assessedoutcome_copy_selector'),

    url(r'^assessed-outcome/(?P<pk>\d+)/$',
        views.AssessedOutcomeDetail.as_view(),
        name='assessedoutcome_detail'),

    url(r'^assessed-outcome/(?P<pk>\d+)/update/$',
        views.AssessedOutcomeUpdate.as_view(),
        name='assessedoutcome_update'),

    url(r'^assessed-outcome/(?P<pk>\d+)/versions/$',
        views.AssessedOutcomeVersions.as_view(),
        name='assessedoutcome_versions'),

    url(r'^assessed-outcome/(?P<pk>\d+)/delete/$',
        views.AssessedOutcomeDelete.as_view(),
        name='assessedoutcome_delete'),

    # meta-protocol views
    url(r'^study/(?P<pk>\d+)/meta-protocol/create/$',
        views.MetaProtocolCreate.as_view(),
        name='mp_create'),

    url(r'^meta-protocol/(?P<pk>\d+)/$',
        views.MetaProtocolDetail.as_view(),
        name='mp_detail'),

    url(r'^meta-protocol/(?P<pk>\d+)/json/$',
        views.MetaProtocolJSON.as_view(),
        name='mp_json'),

    url(r'^meta-protocol/(?P<pk>\d+)/update/$',
        views.MetaProtocolUpdate.as_view(),
        name='mp_update'),

    url(r'^meta-protocol/(?P<pk>\d+)/delete/$',
        views.MetaProtocolDelete.as_view(),
        name='mp_delete'),

    # meta-result views
    url(r'^assessment/(?P<pk>\d+)/meta-results/$',
        views.MetaResultList.as_view(),
        name='metaresult_list'),

    url(r'^meta-protocol/(?P<pk>\d+)/meta-result/create/$',
        views.MetaResultCreate.as_view(),
        name='mr_create'),

    url(r'^meta-protocol/(?P<pk>\d+)/meta-result/copy-as-new-selector/$',
        views.MetaResultCopyAsNewSelector.as_view(),
        name='mr_copy_selector'),

    url(r'^meta-result/(?P<pk>\d+)/$',
        views.MetaResultDetail.as_view(),
        name='mr_detail'),

    url(r'^meta-result/(?P<pk>\d+)/json/$',
        views.MetaResultJSON.as_view(),
        name='mr_json'),

    url(r'^meta-result/(?P<pk>\d+)/update/$',
        views.MetaResultUpdate.as_view(),
        name='mr_update'),

    url(r'^meta-result/(?P<pk>\d+)/delete/$',
        views.MetaResultDelete.as_view(),
        name='mr_delete'),

    url(r'^api/', include(router.urls)),
]
