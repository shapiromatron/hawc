from django.conf import settings
from rest_framework import serializers

from ..animal.serializers import EndpointSerializer
from ..common.serializers import validate_pydantic
from . import constants, models, tasks


class SessionBmd2Serializer(serializers.ModelSerializer):
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


class SessionBmd3Serializer(serializers.ModelSerializer):
    url_api = serializers.URLField(source="get_api_url")
    url_execute_status = serializers.URLField(source="get_execute_status_url")
    input_options = serializers.JSONField(source="get_input_options")
    endpoint = EndpointSerializer(read_only=True)

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
        extra_kwargs = {"execute": {"write_only": True}}

    def validate_inputs(self, value):
        pydantic_class = constants.get_input_model(self.instance.endpoint)
        validate_pydantic(pydantic_class, "inputs", value)
        return value

    def validate_selected(self, value):
        pydantic_class = constants.SelectedModel
        validate_pydantic(pydantic_class, "selected", value)
        return value

    def save_and_execute(self):
        data = self.validated_data
        instance = self.instance

        # reset model outputs
        instance.dose_units_id = data["inputs"]["dose_units_id"]
        instance.inputs = data["inputs"]
        instance.outputs = {}
        instance.errors = {}
        instance.selected = constants.SelectedModel().dict()
        instance.active = False
        instance.date_executed = None
        instance.save()

        # trigger BMD model execution
        tasks.execute.delay(instance.id)

    def select(self):
        data = self.validated_data
        instance = self.instance

        # deactivate other session
        instance.deactivate_similar_sessions()

        # save hawc selection
        instance.selected = data["selected"]
        instance.active = True

        # set output selection
        serialized = constants.SelectedModel.parse_obj(data["selected"])
        instance.outputs["selected"] = serialized.to_bmd_output()

        instance.save()
