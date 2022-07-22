from django.db import models

from hawc.apps.assessment.models import Assessment


class AssessmentValues(models.Model):
    assessment = models.ForeignKey(Assessment, models.CASCADE)
    value = models.FloatField()
    comments = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
