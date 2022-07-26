import re
from django.db import models

from hawc.apps.assessment.models import Assessment


class AssessmentValues(models.Model):
    assessment = models.ForeignKey(Assessment, models.CASCADE, related_name="values_list")
    value = models.FloatField()
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
