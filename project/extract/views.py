import json
import logging
from rest_framework import permissions, status, viewsets, decorators, filters
from rest_framework.views import APIView
from rest_framework.response import Response

from . import models
from .serializers import SpeciesSerializer, StrainSerializer
from django.apps import apps
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import View, ListView, TemplateView, FormView
from django.views.generic.edit import CreateView
from django.shortcuts import HttpResponse, get_object_or_404

from django.db import connection
from django.core.management.base import BaseCommand, CommandError, OutputWrapper

from assessment.models import Species, Strain

class SpeciesView(APIView):

	def get(self, request, format=None):
		SpeciesResults = apps.get_model('assessment', 'Species').objects.all()
		serializer = SpeciesSerializer(SpeciesResults, many=True)
		return HttpResponse(json.dumps(serializer.data), content_type="application/json")

class StrainView(APIView):

	def get(self, request, format=None):
		StrainResults = apps.get_model('assessment', 'Strain').objects.all()
		serializer = StrainSerializer(StrainResults, many=True)
		return HttpResponse(json.dumps(serializer.data), content_type="application/json")
