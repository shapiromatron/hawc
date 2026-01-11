from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

from ..apps.animal.urls import router as animal_router
from ..apps.assessment import views
from ..apps.assessment.urls import router as assessment_router
from ..apps.bmd.urls import router as bmd_router
from ..apps.common.autocomplete import get_autocomplete
from ..apps.common.urls import router as common_router
from ..apps.eco.urls import router as eco_router
from ..apps.epi.urls import router as epi_router
from ..apps.epimeta.urls import router as epimeta_router
from ..apps.epiv2.urls import router as epiv2_router
from ..apps.hawc_admin.urls import get_admin_urlpatterns
from ..apps.invitro.urls import router as invitro_router
from ..apps.lit.urls import router as lit_router
from ..apps.mgmt.urls import router as mgmt_router
from ..apps.riskofbias.urls import router as riskofbias_router
from ..apps.study.urls import router as study_router
from ..apps.summary.urls import router as summary_router
from ..apps.udf.urls import router as udf_router
from ..apps.vocab.urls import router as vocab_router

urlpatterns = [
    # Portal
    path("", views.Home.as_view(), name="home"),
    path("portal/", views.AssessmentList.as_view(), name="portal"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("about/", views.About.as_view(), name="about"),
    path("resources/", views.Resources.as_view(), name="resources"),
    path("contact/", views.Contact.as_view(), name="contact"),
    path("search/", views.Search.as_view(), name="search"),
    # Apps
    path("user/", include("hawc.apps.myuser.urls")),
    path("assessment/", include("hawc.apps.assessment.urls")),
    path("common/", include("hawc.apps.common.urls")),
    path("study/", include("hawc.apps.study.urls")),
    path("ani/", include("hawc.apps.animal.urls")),
    path("eco/", include("hawc.apps.eco.urls")),
    path("epi/", include("hawc.apps.epi.urls")),
    path("epidemiology/", include("hawc.apps.epiv2.urls")),
    path("epi-meta/", include("hawc.apps.epimeta.urls")),
    path("in-vitro/", include("hawc.apps.invitro.urls")),
    path("udf/", include("hawc.apps.udf.urls")),
    path("bmd/", include("hawc.apps.bmd.urls")),
    path("lit/", include("hawc.apps.lit.urls")),
    path("summary/", include("hawc.apps.summary.urls")),
    path("rob/", include("hawc.apps.riskofbias.urls")),
    path("mgmt/", include("hawc.apps.mgmt.urls")),
    path("vocab/", include("hawc.apps.vocab.urls")),
    # common functionality
    path("update-session/", views.UpdateSession.as_view(), name="update_session"),
    path("rasterize/", views.RasterizeCss.as_view(), name="css-rasterize"),
    path("autocomplete/<str:autocomplete_name>/", get_autocomplete, name="autocomplete"),
    # Error-pages
    path("401/", views.Error401.as_view(), name="401"),
    path("403/", views.Error403.as_view(), name="403"),
    path("404/", views.Error404.as_view(), name="404"),
    path("500/", views.Error500.as_view(), name="500"),
]

# add admin patterns
open_api_patterns = [
    path("ani/api/", include(animal_router.urls)),
    path("assessment/api/", include(assessment_router.urls)),
    path("bmd/api/", include(bmd_router.urls)),
    path("common/api/", include(common_router.urls)),
    path("eco/api/", include(eco_router.urls)),
    path("epi/api/", include(epi_router.urls)),
    path("epi-meta/api/", include(epimeta_router.urls)),
    path("epidemiology/api/", include(epiv2_router.urls)),
    path("in-vitro/api/", include(invitro_router.urls)),
    path("udf/api/", include(udf_router.urls)),
    path("lit/api/", include(lit_router.urls)),
    path("mgmt/api/", include(mgmt_router.urls)),
    path("rob/api/", include(riskofbias_router.urls)),
    path("study/api/", include(study_router.urls)),
    path("summary/api/", include(summary_router.urls)),
    path("vocab/api/", include(vocab_router.urls)),
]
urlpatterns += get_admin_urlpatterns(open_api_patterns)

# only for DEBUG, want to use static server otherwise
if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
