import django.views.static
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
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
    url(r"^ani/api/", include(hawc.apps.animal.urls.router.urls)),
    url(r"^assessment/api/", include(hawc.apps.assessment.urls.router.urls)),
    url(r"^bmd/api/", include(hawc.apps.bmd.urls.router.urls)),
    url(r"^epi/api/", include(hawc.apps.epi.urls.router.urls)),
    url(r"^epi-meta/api/", include(hawc.apps.epimeta.urls.router.urls)),
    url(r"^in-vitro/api/", include(hawc.apps.invitro.urls.router.urls)),
    url(r"^lit/api/", include(hawc.apps.lit.urls.router.urls)),
    url(r"^mgmt/api/", include(hawc.apps.mgmt.urls.router.urls)),
    url(r"^rob/api/", include(hawc.apps.riskofbias.urls.router.urls)),
    url(r"^study/api/", include(hawc.apps.study.urls.router.urls)),
    url(r"^summary/api/", include(hawc.apps.summary.urls.router.urls)),
]

urlpatterns = [
    # Portal
    url(r"^$", views.Home.as_view(), name="home"),
    url(r"^portal/$", views.AssessmentList.as_view(), name="portal"),
    url(
        r"^robots\.txt$",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    url(r"^about/$", views.About.as_view(), name="about"),
    url(r"^contact/$", views.Contact.as_view(), name="contact"),
    # Apps
    url(r"^user/", include("hawc.apps.myuser.urls")),
    url(r"^assessment/", include("hawc.apps.assessment.urls")),
    url(r"^study/", include("hawc.apps.study.urls")),
    url(r"^ani/", include("hawc.apps.animal.urls")),
    url(r"^epi/", include("hawc.apps.epi.urls")),
    url(r"^epi-meta/", include("hawc.apps.epimeta.urls")),
    url(r"^in-vitro/", include("hawc.apps.invitro.urls")),
    url(r"^bmd/", include("hawc.apps.bmd.urls")),
    url(r"^lit/", include("hawc.apps.lit.urls")),
    url(r"^summary/", include("hawc.apps.summary.urls")),
    url(r"^rob/", include("hawc.apps.riskofbias.urls")),
    url(r"^mgmt/", include("hawc.apps.mgmt.urls")),
    url(r"^vocab/", include("hawc.apps.vocab.urls")),
    # Error-pages
    url(r"^403/$", views.Error403.as_view(), name="403"),
    url(r"^404/$", views.Error404.as_view(), name="404"),
    url(r"^500/$", views.Error500.as_view(), name="500"),
    # Changelog
    url(r"^update-session/", views.UpdateSession.as_view(), name="update_session"),
    # Admin
    url(
        rf"^admin/{settings.ADMIN_URL_PREFIX}/dashboard/$",
        views.AdminDashboard.as_view(),
        name="admin_dashboard",
    ),
    url(
        rf"^admin/{settings.ADMIN_URL_PREFIX}/assessment-size/$",
        views.AdminAssessmentSize.as_view(),
        name="admin_assessment_size",
    ),
    url(
        rf"^admin/{settings.ADMIN_URL_PREFIX}/healthcheck/$",
        views.Healthcheck.as_view(),
        name="healthcheck",
    ),
    url(rf"^admin/{settings.ADMIN_URL_PREFIX}/", admin.site.urls),
    url(r"^selectable/", include("selectable.urls")),
    url(
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
        url(r"^__debug__/", include(debug_toolbar.urls)),
        url(
            r"^media/(?P<path>.*)$",
            django.views.static.serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

admin.autodiscover()
