from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import (
    BaseAssessmentViewSet,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..lit.models import Reference
from . import exports, models


class UdfAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    @action(
        detail=True,
        url_path="model-export",
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export_model_udfs(self, request, pk):
        """
        UDF complete model export.

        Must be able to edit objects because this could show data about content which is not
        from a published study.
        """
        assessment: Assessment = self.get_object()
        export_name = f"{assessment}-udf-model"
        qs = models.ModelUDFContent.objects.assessment_qs(assessment)
        content_type = request.query_params.get("content_type", "").split(".")
        if len(content_type) == 2:
            qs = qs.filter_content_type(app=content_type[0], model=content_type[1])
        exporter = exports.ModelUDFContentExporter.flat_export(qs, filename=export_name)
        return Response(exporter)

    @action(
        detail=True,
        url_path="tag-export",
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export_tag_udfs(self, request, pk):
        """
        UDF complete tag export.

        Must be able to edit objects because this could show data about content which is not
        from a published study.
        """
        assessment: Assessment = self.get_object()
        export_name = f"{assessment}-udf-tags"
        qs = models.TagUDFContent.objects.assessment_qs(assessment)
        tag = request.query_params.get("tag", None)
        if tag:
            qs = qs.filter_tag(tag=tag)
        exporter = exports.TagUDFContentExporter.flat_export(qs, filename=export_name)
        return Response(exporter)

    @action(
        detail=True,
        url_path="model-bindings",
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export_model_bindings(self, request, pk):
        assessment: Assessment = self.get_object()
        export_name = f"{assessment}-udf-model_bindings"
        qs = models.ModelBinding.objects.assessment_qs(assessment)
        exporter = exports.ModelBindingContentExporter.flat_export(qs, filename=export_name)
        return Response(exporter)

    @action(
        detail=True,
        url_path="tag-bindings",
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export_tag_bindings(self, request, pk):
        assessment: Assessment = self.get_object()
        export_name = f"{assessment}-udf-tag_bindings"
        qs = models.TagBinding.objects.assessment_qs(assessment)
        exporter = exports.TagBindingContentExporter.flat_export(qs, filename=export_name)
        return Response(exporter)

    @action(
        detail=True,
        url_path="tag",
        methods=("post",),
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
    )
    def tag_content(self, request, pk):
        assessment: Assessment = self.get_object()
        tag_binding = get_object_or_404(models.TagBinding, id=request.data.get("tag_binding", -1))
        reference = get_object_or_404(Reference, id=request.data.get("reference", -1))
        content = request.data.get("content", None)
        if not tag_binding or not reference or not content:
            return Response("Must provide tag_binding, reference, and content", status=400)
        if reference.assessment.pk != assessment.pk or tag_binding.assessment.pk != assessment.pk:
            return Response("Reference and tag binding must be in the assessment.")
        obj, created = models.TagUDFContent.objects.update_or_create(
            reference=reference,
            tag_binding=tag_binding,
            defaults={"content": content},
        )
        return Response(
            {
                "id": obj.id,
                "reference": obj.reference.id,
                "tag_binding": obj.tag_binding.id,
                "content": obj.content,
            }
        )

    @action(
        detail=True,
        url_path="model",
        methods=("post",),
        action_perms=AssessmentViewSetPermissions.CAN_EDIT_OBJECT,
    )
    def model_content(self, request, pk):
        assessment: Assessment = self.get_object()
        model_binding = get_object_or_404(
            models.ModelBinding, id=request.data.get("model_binding", -1)
        )
        content_type = request.data.get("content_type", "").split(".")
        try:
            content_type = get_object_or_404(
                ContentType,
                app_label=content_type[0],
                model=content_type[1],
            )
        except IndexError:
            return Response("Must provide a content_type in the form {app_label}.{model}")
        object_id = request.data.get("object_id", None)
        content_object = content_type.get_object_for_this_type(id=object_id)
        content = request.data.get("content", None)
        if not model_binding or not content_type or not content:
            return Response("Must provide model_binding, content_type, and content", status=400)
        if (
            content_object.get_assessment().pk != assessment.pk
            or model_binding.assessment.pk != assessment.pk
        ):
            return Response("Reference and model binding must be in the assessment.")
        obj, created = models.ModelUDFContent.objects.update_or_create(
            model_binding=model_binding,
            content_type=content_type,
            object_id=object_id,
            defaults={"content": content},
        )
        return Response(
            {
                "id": obj.id,
                "object": obj.content_object.id,
                "model_binding": obj.model_binding.id,
                "content": obj.content,
            }
        )
