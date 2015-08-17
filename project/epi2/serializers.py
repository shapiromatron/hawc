from rest_framework import serializers

from assessment.serializers import EffectTagsSerializer
from study.serializers import StudySerializer

from utils.helper import SerializerHelper

from . import models


class EthnicitySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ethnicity
        fields = ('id', 'name')


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Country
        fields = ('name', 'id')


class StudyPopulationCriteriaSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="criteria.id")
    description = serializers.ReadOnlyField(source="criteria.description")
    criteria_type = serializers.CharField(source='get_criteria_type_display', read_only=True)

    class Meta:
        model = models.StudyPopulationCriteria
        fields = ('id', 'description')


class OutcomeLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = models.Outcome
        fields = ('id', 'name', 'url')


class GroupSerializer(serializers.ModelSerializer):
    ethnicities = EthnicitySerializer(many=True)

    class Meta:
        model = models.Group


class GroupCollectionLinkSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = models.GroupCollection
        fields = ('id', 'name', 'url')


class StudyPopulationSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    criteria = StudyPopulationCriteriaSerializer(source='spcriteria', many=True)
    outcomes = OutcomeLinkSerializer(many=True)
    group_collections = GroupCollectionLinkSerializer(many=True)
    country = serializers.CharField(source='country.name', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    design = serializers.CharField(source='get_design_display', read_only=True)

    class Meta:
        model = models.StudyPopulation


class OutcomeSerializer(serializers.ModelSerializer):
    study_population = StudyPopulationSerializer()
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = models.Outcome


class GroupCollectionSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    study_population = StudyPopulationSerializer()
    groups = GroupSerializer(many=True)

    class Meta:
        model = models.GroupCollection
