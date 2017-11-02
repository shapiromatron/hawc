import json

from django.apps import apps
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from utils.helper import HAWCDjangoJSONEncoder
from utils.models import BaseManager


class SpeciesManager(BaseManager):

    def assessment_qs(self, assessment_id):
        return self.all()

class StrainManager(BaseManager):

    def assessment_qs(self, assessment_id):
        return self.all()

