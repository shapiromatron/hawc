from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views, api


router = DefaultRouter()
router.register(r'study', api.Study, base_name="study")

urlpatterns = [
    url(r'^api/', include(router.urls)),

    # study
    url(r'^assessment/(?P<pk>\d+)/$',
        views.StudyList.as_view(),
        name='list'),
    url(r'^(?P<pk>\d+)/add-details/$',
        views.StudyCreateFromReference.as_view(),
        name='new_study'),
    url(r'^assessment/(?P<pk>\d+)/new-study/$',
        views.ReferenceStudyCreate.as_view(),
        name='new_ref'),
    url(r'^assessment/(?P<pk>\d+)/report/',
        views.StudyReport.as_view(),
        name='studies_report'),
    url(r'^assessment/(?P<pk>\d+)/copy-studies/$',
        views.StudiesCopy.as_view(),
        name='studies_copy'),

    url(r'^(?P<pk>\d+)/$',
        views.StudyRead.as_view(),
        name='detail'),
    url(r'^(?P<pk>\d+)/edit/$',
        views.StudyUpdate.as_view(),
        name='update'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.StudyDelete.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/versions/$',
        views.StudyVersions.as_view(),
        name='versions'),

    # attachment
    url(r'^attachment/(?P<pk>\d+)/$',
        views.AttachmentRead.as_view(),
        name='attachment_detail'),
    url(r'^(?P<pk>\d+)/attachment/add/$',
        views.AttachmentCreate.as_view(),
        name='attachment_create'),
    url(r'^attachment/(?P<pk>\d+)/delete/$',
        views.AttachmentDelete.as_view(),
        name='attachment_delete'),
]
