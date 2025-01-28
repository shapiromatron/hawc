from rest_framework import serializers

from ..assessment.models import LabeledItem
from ..common.helper import SerializerHelper
from ..riskofbias.serializers import AssessmentRiskOfBiasSerializer
from . import constants, models


class CollectionVisualSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url")
    visual_type = serializers.CharField(source="get_visual_type_display")
    data_url = serializers.CharField(source="get_data_url")

    class Meta:
        model = models.Visual
        exclude = ("endpoints",)


class VisualSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance.id != instance.FAKE_INITIAL_ID:
            ret["url"] = instance.get_absolute_url()
            ret["url_update"] = instance.get_update_url()
            ret["url_delete"] = instance.get_delete_url()
            ret["data_url"] = instance.get_data_url()
            ret["label_htmx"] = LabeledItem.get_label_url(instance, "label")
            ret["label_indicators_htmx"] = LabeledItem.get_label_url(instance, "label_indicators")

        if instance.visual_type in [
            constants.VisualType.ROB_HEATMAP,
            constants.VisualType.ROB_BARCHART,
        ]:
            ret["rob_settings"] = AssessmentRiskOfBiasSerializer(instance.assessment).data

        ret["visual_type"] = instance.get_visual_type_display()

        ret["endpoints"] = [
            SerializerHelper.get_serialized(d, json=False) for d in instance.get_endpoints()
        ]

        ret["studies"] = [
            SerializerHelper.get_serialized(d, json=False) for d in instance.get_studies()
        ]

        ret["assessment_rob_name"] = instance.assessment.get_rob_name_display()
        ret["assessment_name"] = str(instance.assessment)

        return ret

    def validate(self, data):
        visual_type = data["visual_type"]
        evidence_type = data["evidence_type"]
        if evidence_type not in constants.VISUAL_EVIDENCE_CHOICES[visual_type]:
            raise serializers.ValidationError(
                {
                    "evidence_type": f"Invalid evidence type {evidence_type} for visual {visual_type}."
                }
            )
        return data

    class Meta:
        model = models.Visual
        exclude = ("endpoints",)


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
