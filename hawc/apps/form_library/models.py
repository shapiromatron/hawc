from django.db import models


# TODO: is this a good name? i changed it from dynamic form because it makes the naming scheme weird
# for the actual form class (DynamicFormForm)
class CustomDataExtraction(models.Model):
    name = models.CharField()
    description = models.TextField()
    schema = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
