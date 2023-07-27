from rest_framework import serializers

from ..common.api import DynamicFieldsMixin
from . import models


class DesignCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Design
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


class CauseCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Cause
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


class EffectCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Effect
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.study.short_citation


class ResultCleanupSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    study_short_citation = serializers.SerializerMethodField()

    class Meta:
        model = models.Result
        cleanup_fields = ("study_short_citation", *model.TEXT_CLEANUP_FIELDS)
        fields = ("id", *cleanup_fields)

    def get_study_short_citation(self, obj):
        return obj.design.study.short_citation
