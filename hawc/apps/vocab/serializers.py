from rest_framework import serializers

from . import models


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Term
        fields = ("id", "name")
