import json
from . import models
from rest_framework import serializers


class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Species
        fields = ('id', 'name', 'created', 'last_updated')

class StrainSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Strain
        fields = ('id', 'species_id', 'name', 'created', 'last_updated')
