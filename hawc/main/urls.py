from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

import hawc.apps.animal.urls
import hawc.apps.animalv2.urls
import hawc.apps.assessment.urls
import hawc.apps.bmd.urls
import hawc.apps.common.urls
import hawc.apps.eco.urls
import hawc.apps.epi.urls
import hawc.apps.epimeta.urls
import hawc.apps.epiv2.urls
import hawc.apps.hawc_admin.urls
import hawc.apps.invitro.urls
import hawc.apps.lit.urls
import hawc.apps.mgmt.urls
import hawc.apps.riskofbias.urls
import hawc.apps.study.urls
import hawc.apps.summary.urls
import hawc.apps.udf.urls
import hawc.apps.vocab.urls
from hawc.apps.assessment import views
from hawc.apps.common.autocomplete import get_autocomplete

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
    # Apps
    path("user/", include("hawc.apps.myuser.urls")),
    path("assessment/", include("hawc.apps.assessment.urls")),
    path("common/", include("hawc.apps.common.urls")),
    path("study/", include("hawc.apps.study.urls")),
    path("ani/", include("hawc.apps.animal.urls")),
    path("animal-bioassay/", include("hawc.apps.animalv2.urls")),
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
    path("docs/", include("hawc.apps.docs.urls")),
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
    path("ani/api/", include(hawc.apps.animal.urls.router.urls)),
    path("assessment/api/", include(hawc.apps.assessment.urls.router.urls)),
    path("bmd/api/", include(hawc.apps.bmd.urls.router.urls)),
    path("common/api/", include(hawc.apps.common.urls.router.urls)),
    path("eco/api/", include(hawc.apps.eco.urls.router.urls)),
    path("epi/api/", include(hawc.apps.epi.urls.router.urls)),
    path("epi-meta/api/", include(hawc.apps.epimeta.urls.router.urls)),
    path("epidemiology/api/", include(hawc.apps.epiv2.urls.router.urls)),
    path("in-vitro/api/", include(hawc.apps.invitro.urls.router.urls)),
    path("lit/api/", include(hawc.apps.lit.urls.router.urls)),
    path("mgmt/api/", include(hawc.apps.mgmt.urls.router.urls)),
    path("rob/api/", include(hawc.apps.riskofbias.urls.router.urls)),
    path("study/api/", include(hawc.apps.study.urls.router.urls)),
    path("summary/api/", include(hawc.apps.summary.urls.router.urls)),
    path("vocab/api/", include(hawc.apps.vocab.urls.router.urls)),
]
urlpatterns += hawc.apps.hawc_admin.urls.get_admin_urlpatterns(open_api_patterns)

# only for DEBUG, want to use static server otherwise
if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
