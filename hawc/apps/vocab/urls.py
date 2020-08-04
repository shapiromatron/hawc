from django.conf.urls import url
from django.contrib import admin

from . import views

app_name = "vocab"
urlpatterns = [
    url(r"^widget/$", views.Widget.as_view(), name="widget"),
]

admin.autodiscover()
