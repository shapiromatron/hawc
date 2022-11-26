from rest_framework import serializers

from . import constants, models


class SessionSerializer(serializers.ModelSerializer):
    model_options = serializers.JSONField(source="get_model_options", read_only=True)
    bmr_options = serializers.JSONField(source="get_bmr_options", read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["logic"] = constants.bmds2_logic()
        return ret

    class Meta:
        model = models.Session
        fields = (
            "id",
            "endpoint",
            "dose_units",
            "version",
            "active",
            "is_finished",
            "date_executed",
            "created",
            "last_updated",
            "inputs",
            "outputs",
            "errors",
            "selected",
            "model_options",
            "bmr_options",
        )
