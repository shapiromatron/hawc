from django.db import models


# TODO: is this a good name? i changed it from dynamic form because it makes the naming scheme weird
# for the actual form class
class CustomDataExtraction(models.Model):
    name = models.CharField()
    description = models.TextField()
    schema = models.JSONField()
