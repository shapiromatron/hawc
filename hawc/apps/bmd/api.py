from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import BaseAssessmentViewSet
from ..assessment.constants import AssessmentViewSetPermissions
from ..common.serializers import UnusedSerializer
from . import models, serializers


class Session(BaseAssessmentViewSet):
    http_method_names = ["get", "patch"]
    assessment_filter_args = "endpoint__assessment"
    model = models.Session
    serializer_class = UnusedSerializer

    def get_queryset(self):
        return self.model.objects.all().select_related("endpoint")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.version.startswith("BMDS2"):
            serializer = serializers.SessionBmd2Serializer(instance)
        else:
            serializer = serializers.SessionBmd3Serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_bmds_version2():
            raise exceptions.ValidationError("Cannot modify legacy BMD analyses")
        serializer = serializers.SessionBmdUpdateSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        action = request.data.get("action")
        if action == "execute":
            serializer.save_and_execute()
        elif action == "select":
            serializer.select()
        return Response({"status": "success", "id": instance.id})

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["get"],
        url_path="execute-status",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
    )
    def execute_status(self, request, pk=None):
        instance = self.get_object()
        if instance.is_bmds_version2():
            raise exceptions.ValidationError("Cannot modify legacy BMD analyses")
        SerializerClass = (
            serializers.SessionBmd3Serializer
            if instance.is_finished
            else serializers.SessionBmd3StatusSerializer
        )
        serializer = SerializerClass(instance)
        return Response(serializer.data)
