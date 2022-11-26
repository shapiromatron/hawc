from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import AssessmentViewset
from . import models, serializers


class Session(AssessmentViewset):
    assessment_filter_args = "endpoint__assessment"
    model = models.Session
    lookup_value_regex = r"\d+"
    serializer_class = serializers.SessionSerializer

    def get_serializer_class(self):
        if self.action == "execute":
            # TODO - BMDS3 - reimplement after integration
            return serializers.SessionSerializer
        elif self.action == "selected_model":
            # TODO - BMDS3 - reimplement after integration
            return serializers.SessionSerializer
        else:
            return serializers.SessionSerializer

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        # TODO - BMDS3 - reimplement after integration
        instance = self.get_object()
        # serializer = self.get_serializer(instance, data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # tasks.execute.delay(instance.id)
        return Response({"started": True, "id": instance.id})

    @action(detail=True, methods=["get"])
    def execute_status(self, request, pk=None):
        # TODO - BMDS3 - reimplement after integration
        # ping until execution is complete
        session = self.get_object()
        return Response({"finished": session.is_finished})

    @action(detail=True, methods=("post",))
    def selected_model(self, request, pk=None):
        # TODO - BMDS3 - reimplement after integration
        instance = self.get_object()
        # serializer = self.get_serializer(data=request.data, context={"session": instance})
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        return Response({"status": True, "id": instance.id})
