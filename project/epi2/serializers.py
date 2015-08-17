from rest_framework import serializers

from assessment.serializers import EffectTagsSerializer
from study.serializers import StudySerializer

from utils.helper import SerializerHelper

from . import models


class StudyPopulationCriteriaSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="criteria.id")
    description = serializers.ReadOnlyField(source="criteria.description")

    def to_representation(self, instance):
        ret = super(StudyPopulationCriteriaSerializer, self).to_representation(instance)
        ret["criteria_type"] = instance.get_criteria_type_display()
        return ret

    class Meta:
        model = models.StudyPopulationCriteria
        fields = ('id', 'description')


class OutcomeLinkSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(OutcomeLinkSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Outcome
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Group


class GroupCollectionLinkSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(GroupCollectionLinkSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.GroupCollection
        fields = ('id', 'name')


class StudyPopulationSerializer(serializers.ModelSerializer):
    study = StudySerializer()
    criteria = StudyPopulationCriteriaSerializer(source='spcriteria', many=True)
    outcomes = OutcomeLinkSerializer(many=True)
    group_collections = GroupCollectionLinkSerializer(many=True)

    def to_representation(self, instance):
        ret = super(StudyPopulationSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.StudyPopulation


class OutcomeSerializer(serializers.ModelSerializer):
    study_population = StudyPopulationSerializer()

    def to_representation(self, instance):
        ret = super(OutcomeSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Outcome


class GroupCollectionSerializer(serializers.ModelSerializer):
    study_population = StudyPopulationSerializer()
    groups = GroupSerializer(many=True)

    def to_representation(self, instance):
        ret = super(GroupCollectionSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.GroupCollection
