import django.views.static
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from hawc.apps.assessment import views

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
    # Error-pages
    url(r"^403/$", views.Error403.as_view(), name="403"),
    url(r"^404/$", views.Error404.as_view(), name="404"),
    url(r"^500/$", views.Error500.as_view(), name="500"),
    # Changelog
    url(r"^update-session/", views.UpdateSession.as_view(), name="update_session"),
    # Admin
    url(rf"^admin/{settings.ADMIN_URL_PREFIX}/", include(admin.site.urls)),
    url(r"^selectable/", include("selectable.urls")),
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
