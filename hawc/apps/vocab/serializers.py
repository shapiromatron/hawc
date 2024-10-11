import json
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

from ..common.serializers import BulkSerializer
from . import models


class TermBulkSerializer(BulkSerializer):
    def values_equal(self, instance, field, value):
        # equality for deprecated_on is whether it needs to be set
        if field == "deprecated_on":
            return bool(instance.deprecated_on) == bool(value)
        return super().values_equal(instance, field, value)


class TermSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    parent_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    deprecated = serializers.BooleanField(required=False, write_only=True)

    def validate(self, data):
        deprecated = data.pop("deprecated", None)
        if deprecated is not None:
            data["deprecated_on"] = timezone.now() if deprecated else None
        return data

    class Meta:
        model = models.Term
        fields = "__all__"
        list_serializer_class = TermBulkSerializer


class SimpleTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Term
        fields = ("id", "name")


class EntitySerializer(serializers.ModelSerializer):
    def get_unique_together_validators(self):
        return []

    class Meta:
        model = models.Entity
        fields = ("id", "ontology", "uid")


class GuidelineProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GuidelineProfile
        fields = "_all_"

    def validate_guideline_profile_id(self, guideline_id):
        # validate guideline profile
        if guideline_id:
            valid_guidelines = self._load_guideline_data()
            ids = [guideline["guideline_id"] for guideline in valid_guidelines]
            if guideline_id not in ids:
                raise ValidationError(f"{guideline_id} is not a valid guideline")

        return guideline_id

    def _load_guideline_data() -> dict:
        """Return guideline fixture data."""
        p = Path(settings.PROJECT_PATH) / "apps/vocab/fixtures/guidelines.json"
        return json.loads(p.read_text())
