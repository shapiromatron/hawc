from rest_framework import serializers

from . import models


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Term
        fields = ("id", "name")


class EntitySerializer(serializers.ModelSerializer):
    def get_unique_together_validators(self):
        return []

    class Meta:
        model = models.Entity
        fields = ("id", "ontology", "uid")
