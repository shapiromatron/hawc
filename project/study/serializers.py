from rest_framework import serializers

from lit.serializers import IdentifiersSerializer, ReferenceTagsSerializer
from utils.helper import SerializerHelper

from . import models


class StudyQualitySerializer(serializers.ModelSerializer):
    study = serializers.PrimaryKeyRelatedField()
    score_description = serializers.CharField(source='get_score_display', read_only=True)

    class Meta:
        model = models.StudyQuality
        depth = 2


class StudySerializer(serializers.ModelSerializer):

    url = serializers.CharField(source='get_absolute_url', read_only=True)

    def transform_study_type(self, obj, value):
        return obj.get_study_type_display()

    def transform_coi_reported(self, obj, value):
        return obj.get_coi_reported_display()

    class Meta:
        model = models.Study
        depth = 0


class VerboseStudySerializer(StudySerializer):
    assessment = serializers.PrimaryKeyRelatedField()
    searches = serializers.PrimaryKeyRelatedField(many=True)
    qualities = StudyQualitySerializer(many=True)
    identifiers = IdentifiersSerializer(many=True)
    tags = ReferenceTagsSerializer()

    class Meta:
        model = models.Study
        depth = 1


SerializerHelper.add_serializer(models.Study, VerboseStudySerializer)
