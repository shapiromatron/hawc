from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import BaseAssessmentViewSet
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.helper import tryParseInt
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer, validate_pydantic
from . import exports, models, schemas


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
        if tag_id := tryParseInt(request.query_params.get("tag")):
            qs = qs.filter_tag(tag_id=tag_id)
        # TODO - filter to only show resolved tags
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
        validated_data = validate_pydantic(
            schemas.ModifyTagUDFContent,
            field=None,
            data={"assessment": assessment.id, **request.data},
        )
        instance, _ = models.TagUDFContent.objects.update_or_create(
            reference=validated_data.reference_obj,
            tag_binding=validated_data.tag_binding_obj,
            defaults={"content": validated_data.content},
        )
        return Response(
            {
                "id": instance.id,
                "reference": instance.reference.id,
                "tag_binding": instance.tag_binding.id,
                "content": instance.content,
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
        validated_data = validate_pydantic(
            schemas.ModifyModelUDFContent,
            field=None,
            data={"assessment": assessment.id, **request.data},
        )
        instance, _ = models.ModelUDFContent.objects.update_or_create(
            model_binding=validated_data.binding_obj,
            content_type=validated_data.content_type_obj,
            object_id=validated_data.obj.id,
            defaults={"content": validated_data.content},
        )
        return Response(
            {
                "id": instance.id,
                "content_type": validated_data.content_type,
                "object_id": instance.object_id,
                "model_binding": instance.model_binding_id,
                "content": instance.content,
            }
        )
