import django.views.static
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.schemas import get_schema_view

import hawc.apps.animal.urls
import hawc.apps.assessment.urls
import hawc.apps.bmd.urls
import hawc.apps.epi.urls
import hawc.apps.epimeta.urls
import hawc.apps.invitro.urls
import hawc.apps.lit.urls
import hawc.apps.mgmt.urls
import hawc.apps.riskofbias.urls
import hawc.apps.study.urls
import hawc.apps.summary.urls
from hawc import __version__
from hawc.apps.assessment import views

open_api_patterns = [
    path("ani/api/", include(hawc.apps.animal.urls.router.urls)),
    path("assessment/api/", include(hawc.apps.assessment.urls.router.urls)),
    path("bmd/api/", include(hawc.apps.bmd.urls.router.urls)),
    path("epi/api/", include(hawc.apps.epi.urls.router.urls)),
    path("epi-meta/api/", include(hawc.apps.epimeta.urls.router.urls)),
    path("in-vitro/api/", include(hawc.apps.invitro.urls.router.urls)),
    path("lit/api/", include(hawc.apps.lit.urls.router.urls)),
    path("mgmt/api/", include(hawc.apps.mgmt.urls.router.urls)),
    path("rob/api/", include(hawc.apps.riskofbias.urls.router.urls)),
    path("study/api/", include(hawc.apps.study.urls.router.urls)),
    path("summary/api/", include(hawc.apps.summary.urls.router.urls)),
]

urlpatterns = [
    # Portal
    path("", views.Home.as_view(), name="home"),
    path("portal/", views.AssessmentList.as_view(), name="portal"),
    path(
        "robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("about/", views.About.as_view(), name="about"),
    path("contact/", views.Contact.as_view(), name="contact"),
    # Apps
    path("user/", include("hawc.apps.myuser.urls")),
    path("assessment/", include("hawc.apps.assessment.urls")),
    path("study/", include("hawc.apps.study.urls")),
    path("ani/", include("hawc.apps.animal.urls")),
    path("epi/", include("hawc.apps.epi.urls")),
    path("epi-meta/", include("hawc.apps.epimeta.urls")),
    path("in-vitro/", include("hawc.apps.invitro.urls")),
    path("bmd/", include("hawc.apps.bmd.urls")),
    path("lit/", include("hawc.apps.lit.urls")),
    path("summary/", include("hawc.apps.summary.urls")),
    path("rob/", include("hawc.apps.riskofbias.urls")),
    path("mgmt/", include("hawc.apps.mgmt.urls")),
    path("vocab/", include("hawc.apps.vocab.urls")),
    # Error-pages
    path("403/", views.Error403.as_view(), name="403"),
    path("404/", views.Error404.as_view(), name="404"),
    path("500/", views.Error500.as_view(), name="500"),
    # Changelog
    path("update-session/", views.UpdateSession.as_view(), name="update_session"),
    # Admin
    path(
        f"admin/{settings.ADMIN_URL_PREFIX}/dashboard/",
        views.AdminDashboard.as_view(),
        name="admin_dashboard",
    ),
    path(
        f"admin/{settings.ADMIN_URL_PREFIX}/assessment-size/",
        views.AdminAssessmentSize.as_view(),
        name="admin_assessment_size",
    ),
    path(
        f"admin/{settings.ADMIN_URL_PREFIX}/healthcheck/",
        views.Healthcheck.as_view(),
        name="healthcheck",
    ),
    path(f"admin/{settings.ADMIN_URL_PREFIX}/", admin.site.urls),
    path("selectable/", include("selectable.urls")),
    path(
        "openapi/",
        get_schema_view(
            title="HAWC",
            version=__version__,
            patterns=open_api_patterns,
            permission_classes=(permissions.IsAdminUser,),
        ),
        name="openapi",
    ),
]

# only for DEBUG, want to use static server otherwise
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path(
            "media/<path:str>", django.views.static.serve, {"document_root": settings.MEDIA_ROOT},
        ),
    ]

admin.autodiscover()
