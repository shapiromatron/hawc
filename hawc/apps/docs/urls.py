from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("documents/", include(wagtaildocs_urls)),
    path("pages/", include(wagtail_urls)),
]
