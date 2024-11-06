from django.db import transaction
from rest_framework import serializers

from ..common.serializers import validate_pydantic
from . import constants, models, tasks


class SessionBmd2Serializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        defaults = constants.bmds2_defaults()
        ret.update(
            logic=defaults["logic"],
            model_options=defaults["model_options"][instance.endpoint.data_type],
            bmr_options=defaults["bmr_options"][instance.endpoint.data_type],
        )
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
        )


class SessionBmd3Serializer(serializers.ModelSerializer):
    url_api = serializers.URLField(source="get_api_url")
    url_execute_status = serializers.URLField(source="get_execute_status_url")
    input_options = serializers.JSONField(source="get_input_options")
    endpoint = serializers.JSONField(source="get_endpoint_serialized", read_only=True)

    class Meta:
        model = models.Session
        fields = (
            "id",
            "url_api",
            "url_execute_status",
            "input_options",
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
        )


class SessionBmd3StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Session
        fields = (
            "id",
            "is_finished",
            "date_executed",
            "created",
            "last_updated",
        )


class SessionBmd3UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Session
        fields = (
            "id",
            "is_finished",
            "date_executed",
            "created",
            "last_updated",
            "inputs",
            "outputs",
            "errors",
            "selected",
        )
        read_only_fields = ["outputs"]
        extra_kwargs = {"action": {"write_only": True}}

    def validate_inputs(self, value):
        validate_pydantic(constants.BmdInputSettings, "inputs", value)
        return value

    def validate_selected(self, value):
        validate_pydantic(constants.SelectedModel, "selected", value)
        return value

    def save_and_execute(self):
        self.instance.dose_units_id = self.validated_data["inputs"]["settings"]["dose_units_id"]
        self.instance.inputs = self.validated_data["inputs"]
        self.instance.reset_execution()
        self.instance.save()

        # trigger BMD model execution
        tasks.execute.delay(self.instance.id)

    @transaction.atomic
    def select(self):
        # deactivate other session
        self.instance.deactivate_similar_sessions()

        # set selected model
        selected = constants.SelectedModel.model_validate(self.validated_data["selected"])
        self.instance.set_selected_model(selected)
        self.instance.save()
