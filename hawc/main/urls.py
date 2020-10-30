import django.views.static
from django.conf import settings
from django.contrib import admin
from django.urls import include, re_path
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
    re_path(r"^ani/api/", include(hawc.apps.animal.urls.router.urls)),
    re_path(r"^assessment/api/", include(hawc.apps.assessment.urls.router.urls)),
    re_path(r"^bmd/api/", include(hawc.apps.bmd.urls.router.urls)),
    re_path(r"^epi/api/", include(hawc.apps.epi.urls.router.urls)),
    re_path(r"^epi-meta/api/", include(hawc.apps.epimeta.urls.router.urls)),
    re_path(r"^in-vitro/api/", include(hawc.apps.invitro.urls.router.urls)),
    re_path(r"^lit/api/", include(hawc.apps.lit.urls.router.urls)),
    re_path(r"^mgmt/api/", include(hawc.apps.mgmt.urls.router.urls)),
    re_path(r"^rob/api/", include(hawc.apps.riskofbias.urls.router.urls)),
    re_path(r"^study/api/", include(hawc.apps.study.urls.router.urls)),
    re_path(r"^summary/api/", include(hawc.apps.summary.urls.router.urls)),
]

urlpatterns = [
    # Portal
    re_path(r"^$", views.Home.as_view(), name="home"),
    re_path(r"^portal/$", views.AssessmentList.as_view(), name="portal"),
    re_path(
        r"^robots\.txt$",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    re_path(r"^about/$", views.About.as_view(), name="about"),
    re_path(r"^contact/$", views.Contact.as_view(), name="contact"),
    # Apps
    re_path(r"^user/", include("hawc.apps.myuser.urls")),
    re_path(r"^assessment/", include("hawc.apps.assessment.urls")),
    re_path(r"^study/", include("hawc.apps.study.urls")),
    re_path(r"^ani/", include("hawc.apps.animal.urls")),
    re_path(r"^epi/", include("hawc.apps.epi.urls")),
    re_path(r"^epi-meta/", include("hawc.apps.epimeta.urls")),
    re_path(r"^in-vitro/", include("hawc.apps.invitro.urls")),
    re_path(r"^bmd/", include("hawc.apps.bmd.urls")),
    re_path(r"^lit/", include("hawc.apps.lit.urls")),
    re_path(r"^summary/", include("hawc.apps.summary.urls")),
    re_path(r"^rob/", include("hawc.apps.riskofbias.urls")),
    re_path(r"^mgmt/", include("hawc.apps.mgmt.urls")),
    re_path(r"^vocab/", include("hawc.apps.vocab.urls")),
    # Error-pages
    re_path(r"^403/$", views.Error403.as_view(), name="403"),
    re_path(r"^404/$", views.Error404.as_view(), name="404"),
    re_path(r"^500/$", views.Error500.as_view(), name="500"),
    # Changelog
    re_path(r"^update-session/", views.UpdateSession.as_view(), name="update_session"),
    # Admin
    re_path(
        rf"^admin/{settings.ADMIN_URL_PREFIX}/dashboard/$",
        views.AdminDashboard.as_view(),
        name="admin_dashboard",
    ),
    re_path(
        rf"^admin/{settings.ADMIN_URL_PREFIX}/assessment-size/$",
        views.AdminAssessmentSize.as_view(),
        name="admin_assessment_size",
    ),
    re_path(
        rf"^admin/{settings.ADMIN_URL_PREFIX}/healthcheck/$",
        views.Healthcheck.as_view(),
        name="healthcheck",
    ),
    re_path(rf"^admin/{settings.ADMIN_URL_PREFIX}/", admin.site.urls),
    re_path(r"^selectable/", include("selectable.urls")),
    re_path(
        r"^openapi/$",
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
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
        re_path(
            r"^media/(?P<path>.*)$",
            django.views.static.serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

admin.autodiscover()
