from django.db import models


class BindingType(models.TextChoices):
    TAG = "tag"
    MODEL = "model"


# Models that are able to be linked to User Defined Fields
SUPPORTED_MODELS = ("animal.endpoint", "study.study")
