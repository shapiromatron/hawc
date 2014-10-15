from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponse

from assessment import views

urlpatterns = patterns('',
    # Portal
    #--------
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^portal/$', views.AssessmentPortal.as_view(), name='portal'),
    url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),
    url(r'^documentation/$', views.Documentation.as_view(), name='documentation'),
    url(r'^contact-us/$', views.ContactUs.as_view(), name='contact'),

    # Apps
    #------
    (r'^user/', include('myuser.urls', namespace='user')),
    (r'^assessment/', include('assessment.urls', namespace='assessment')),
    (r'^study/', include('study.urls', namespace='study')),
    (r'^ani/', include('animal.urls', namespace='animal')),
    (r'^epi/', include('epi.urls', namespace='epi')),
    (r'^in-vitro/', include('invitro.urls', namespace='invitro')),
    (r'^bmd/', include('bmd.urls', namespace='bmd')),
    (r'^lit/', include('lit.urls', namespace='lit')),
    (r'^summary/', include('summary.urls', namespace='summary')),
    (r'^data-pivot/', include('data_pivot.urls', namespace='data_pivot')),
    (r'^comments/', include('comments.urls', namespace='comments')),

    # Error-page testing
    #-------------------
    url(r'^403/$', views.Error403.as_view(), name='403'),
    url(r'^404/$', views.Error404.as_view(), name='404'),
    url(r'^500/$', views.Error500.as_view(), name='500'),

    # Change-log
    url(r'^change-log/$', views.ChangeLogList.as_view(), name='change_log'),
    url(r'^change-log/(?P<slug>[\w-]+)/$', views.ChangeLogDetail.as_view(), name='change_log_detail'),

    # Admin
    #------
    url(r'^admin/', include(admin.site.urls), name='master_admin'),
    url(r'^selectable/', include('selectable.urls')),

    # API
    #-----
    url(r'^api/', include('api.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

# only for DEBUG, want to use static server otherwise
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, }),
   )

admin.autodiscover()
