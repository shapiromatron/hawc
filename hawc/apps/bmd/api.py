from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import AssessmentViewset
from . import models, serializers, tasks


class Session(AssessmentViewset):
    assessment_filter_args = "endpoint__assessment"
    model = models.Session
    lookup_value_regex = r"\d+"

    def get_serializer_class(self):
        if self.action == "execute":
            return serializers.SessionUpdateSerializer
        elif self.action == "selected_model":
            return serializers.SelectedModelUpdateSerializer
        else:
            return serializers.SessionSerializer

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        tasks.execute.delay(instance.id)
        return Response({"started": True})

    @action(detail=True, methods=["get"])
    def execute_status(self, request, pk=None):
        # ping until execution is complete
        session = self.get_object()
        return Response({"finished": session.is_finished})

    @action(detail=True, methods=("post",))
    def selected_model(self, request, pk=None):
        session = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"session": session})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": True})
