from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from assessment import views

urlpatterns = [

    # Portal
    url(r'^$',
        views.Home.as_view(), name='home'),
    url(r'^portal/$',
        views.AssessmentList.as_view(), name='portal'),
    url(r'^robots\.txt$',
        TemplateView.as_view(template_name='robots.txt',
                             content_type='text/plain')),
    url(r'^about/$',
        views.About.as_view(), name='about'),
    url(r'^contact/$',
        views.Contact.as_view(), name='contact'),

    # Apps
    url(r'^user/',
        include('myuser.urls', namespace='user')),
    url(r'^assessment/',
        include('assessment.urls', namespace='assessment')),
    url(r'^study/',
        include('study.urls', namespace='study')),
    url(r'^ani/',
        include('animal.urls', namespace='animal')),
    url(r'^epi/',
        include('epi.urls', namespace='epi')),
    url(r'^epi-meta/',
        include('epimeta.urls', namespace='meta')),
    url(r'^in-vitro/',
        include('invitro.urls', namespace='invitro')),
    url(r'^bmd/',
        include('bmd.urls', namespace='bmd')),
    url(r'^lit/',
        include('lit.urls', namespace='lit')),
    url(r'^summary/',
        include('summary.urls', namespace='summary')),
    url(r'^comments/',
        include('comments.urls', namespace='comments')),
    url(r'^rob/',
        include('riskofbias.urls', namespace='riskofbias')),

    # Error-pages
    url(r'^403/$',
        views.Error403.as_view(), name='403'),
    url(r'^404/$',
        views.Error404.as_view(), name='404'),
    url(r'^500/$',
        views.Error500.as_view(), name='500'),

    # Change-log
    url(r'^update-session/',
        views.UpdateSession.as_view(), name='update_session'),
    url(r'^change-log/$',
        views.ChangeLogList.as_view(), name='change_log'),
    url(r'^change-log/(?P<slug>[\w-]+)/$',
        views.ChangeLogDetail.as_view(), name='change_log_detail'),

    # Admin
    url(r'^admin/',
        include(admin.site.urls), name='master_admin'),
    url(r'^selectable/',
        include('selectable.urls')),
]

# only for DEBUG, want to use static server otherwise
if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, }),
    ]

admin.autodiscover()
