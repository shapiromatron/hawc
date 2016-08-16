from rest_framework import serializers

from lit.serializers import IdentifiersSerializer, ReferenceTagsSerializer
from riskofbias.serializers import RiskOfBiasSerializer
from utils.api import DynamicFieldsMixin
from utils.helper import SerializerHelper

from . import models


class StudySerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(StudySerializer, self).to_representation(instance)
        ret['coi_reported'] = instance.get_coi_reported_display()
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Study


class SimpleStudySerializer(StudySerializer):

    class Meta:
        model = models.Study
        exclude = ('searches', 'identifiers', )


class VerboseStudySerializer(StudySerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    searches = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    riskofbiases = RiskOfBiasSerializer(many=True, read_only=True)
    identifiers = IdentifiersSerializer(many=True)
    tags = ReferenceTagsSerializer()

    class Meta:
        model = models.Study


class FinalRobStudySerializer(StudySerializer):
    assessment = serializers.PrimaryKeyRelatedField(read_only=True)
    riskofbiases = RiskOfBiasSerializer(many=True, read_only=True)

    class Meta:
        model = models.Study
        exclude = ('searches', 'identifiers', )

    def to_representation(self, instance):
        instance.riskofbiases = instance.riskofbiases.filter(final=True)
        ret = super(FinalRobStudySerializer, self).to_representation(instance)
        return ret


class StudyCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = models.Study
        cleanup_fields = model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ('id', )


SerializerHelper.add_serializer(models.Study, VerboseStudySerializer)
