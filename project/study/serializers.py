from rest_framework import serializers

from lit.serializers import IdentifiersSerializer, ReferenceTagsSerializer
from utils.helper import SerializerHelper

from . import models


class StudyQualityDomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.StudyQualityDomain


class StudyQualityMetricSerializer(serializers.ModelSerializer):
    domain = StudyQualityDomainSerializer(read_only=True)

    class Meta:
        model = models.StudyQualityMetric


class StudyQualitySerializer(serializers.ModelSerializer):
    metric = StudyQualityMetricSerializer(read_only=True)

    def to_representation(self, instance):
        ret = super(StudyQualitySerializer, self).to_representation(instance)
        ret['score_description'] = instance.get_score_display()
        ret['score_symbol'] = instance.get_score_symbol()
        ret['url_edit'] = instance.get_edit_url()
        ret['url_delete'] = instance.get_delete_url()
        return ret

    class Meta:
        model = models.StudyQuality
        exclude = ('object_id', 'content_type')


class StudySerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(StudySerializer, self).to_representation(instance)
        ret['study_type'] = instance.get_study_type_display()
        ret['coi_reported'] = instance.get_coi_reported_display()
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Study


class VerboseStudySerializer(StudySerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    searches = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    qualities = StudyQualitySerializer(many=True, read_only=True)
    identifiers = IdentifiersSerializer(many=True)
    tags = ReferenceTagsSerializer()

    class Meta:
        model = models.Study


SerializerHelper.add_serializer(models.Study, VerboseStudySerializer)
