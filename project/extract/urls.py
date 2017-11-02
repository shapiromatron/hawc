from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from . import views, api

#router = DefaultRouter()
#router.register(r'species', views.SpeciesView.as_view())
#router.register(r'strain', views.StrainView.as_view())

urlpatterns = [
	# test to show app is working
    url(r'^species/$', views.SpeciesView.as_view()),
    url(r'^strain/$', views.StrainView.as_view()),

]