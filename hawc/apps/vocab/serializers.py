from rest_framework import serializers
from ..common.serializers import BulkSerializer
from . import models


class TermSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.Term
        fields = "__all__"
        list_serializer_class = BulkSerializer


class EntitySerializer(serializers.ModelSerializer):
    def get_unique_together_validators(self):
        return []

    class Meta:
        model = models.Entity
        fields = ("id", "ontology", "uid")
