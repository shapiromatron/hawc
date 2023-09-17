from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from ..common import validators
from ..common.helper import SerializerHelper
from ..riskofbias.serializers import AssessmentRiskOfBiasSerializer
from . import constants, models


class CollectionDataPivotSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url")
    visual_type = serializers.CharField(source="get_visual_type_display")

    class Meta:
        model = models.DataPivot
        fields = ("id", "title", "url", "visual_type")


class DataPivotSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url")
    data_url = serializers.CharField(source="get_data_url")
    download_url = serializers.CharField(source="get_download_url")
    visual_type = serializers.CharField(source="get_visual_type_display")

    class Meta:
        model = models.DataPivot
        fields = "__all__"


class CollectionVisualSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url")
    visual_type = serializers.CharField(source="get_visual_type_display")
    data_url = serializers.CharField(source="get_data_url")

    class Meta:
        model = models.Visual
        exclude = ("endpoints",)


class VisualSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url")
    visual_type = serializers.CharField(source="get_visual_type_display")
    settings = serializers.JSONField(source="get_settings")
    data_url = serializers.CharField(source="get_data_url")

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance.id != instance.FAKE_INITIAL_ID:
            ret["url"] = instance.get_absolute_url()
            ret["url_update"] = instance.get_update_url()
            ret["url_delete"] = instance.get_delete_url()

        if instance.visual_type in [
            constants.VisualType.ROB_HEATMAP,
            constants.VisualType.ROB_BARCHART,
        ]:
            ret["rob_settings"] = AssessmentRiskOfBiasSerializer(instance.assessment).data

        ret["endpoints"] = [
            SerializerHelper.get_serialized(d, json=False) for d in instance.get_endpoints()
        ]

        ret["studies"] = [
            SerializerHelper.get_serialized(d, json=False) for d in instance.get_studies()
        ]

        ret["assessment_rob_name"] = instance.assessment.get_rob_name_display()
        ret["assessment_name"] = str(instance.assessment)

        return ret

    class Meta:
        model = models.Visual
        exclude = ("slug", "endpoints")


class SummaryTextSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=models.SummaryText.objects.all(), write_only=True
    )
    sibling = serializers.PrimaryKeyRelatedField(
        queryset=models.SummaryText.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = models.SummaryText
        fields = "__all__"
        read_only_fields = ("depth", "path")

    def validate_text(self, value):
        validators.validate_hyperlinks(value)
        return validators.clean_html(value)

    def validate(self, data):
        assessment = data["assessment"]
        parent = data.get("parent")
        if parent and parent.assessment != assessment:
            raise ValidationError({"parent": "Parent must be from the same assessment"})

        sibling = data.get("sibling")
        if sibling and sibling.assessment != assessment:
            raise ValidationError({"sibling": "Sibling must be from the same assessment"})

        return data

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)
        sibling = validated_data.pop("sibling", None)
        instance = models.SummaryText(**validated_data)
        if sibling:
            return sibling.add_sibling(pos="right", instance=instance)
        else:
            sibling = parent.get_first_child()
            if sibling:
                return sibling.add_sibling(pos="first-sibling", instance=instance)
            else:
                return parent.add_child(instance=instance)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.title = validated_data["title"]
        instance.slug = validated_data["slug"]
        instance.text = validated_data["text"]
        instance.save()

        parent = validated_data.get("parent")
        sibling = validated_data.get("sibling", None)
        if sibling:
            if instance.get_prev_sibling() != sibling:
                instance.move(sibling, pos="right")
        elif parent:
            instance.move(parent, pos="first-child")

        return instance


class SummaryTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SummaryTable
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.id:
            ret["url"] = instance.get_absolute_url()
        return ret

    def validate(self, data):
        # check model level validation
        models.SummaryTable(**data).clean()
        return data


SerializerHelper.add_serializer(models.Visual, VisualSerializer)
