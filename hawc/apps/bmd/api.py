from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import BaseAssessmentViewset
from . import models, serializers


class Session(BaseAssessmentViewset):
    assessment_filter_args = "endpoint__assessment"
    model = models.Session

    def get_queryset(self):
        return (
            self.model.objects.all()
            .select_related("endpoint__animal_group__experiment__study")
            .prefetch_related(
                "endpoint__effects",
                "endpoint__groups",
                "endpoint__animal_group__dosing_regime__doses__dose_units",
                "endpoint__animal_group__experiment__study__searches",
                "endpoint__animal_group__experiment__study__identifiers",
            )
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.version.startswith("BMDS2"):
            serializer = serializers.SessionBmd2Serializer(instance)
        else:
            serializer = serializers.SessionBmd3Serializer(instance)
        return Response(serializer.data)

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
