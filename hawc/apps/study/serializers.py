from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions, serializers

from ..assessment.serializers import AssessmentMiniSerializer
from ..common.api import DynamicFieldsMixin
from ..common.helper import SerializerHelper
from ..common.serializers import IdLookupMixin
from ..lit.models import Reference
from ..lit.serializers import IdentifiersSerializer, ReferenceTagsSerializer
from ..riskofbias.serializers import AssessmentRiskOfBiasSerializer, RiskOfBiasSerializer
from . import models


class StudySerializer(IdLookupMixin, serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["coi_reported"] = instance.get_coi_reported_display()
        ret["url"] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Study
        fields = "__all__"


class SimpleStudySerializer(StudySerializer):
    def validate(self, data):
        if "reference_id" in self.initial_data:

            ref_id = self.initial_data.get("reference_id")

            try:
                Reference.objects.get(id=ref_id)
            except ValueError:
                raise serializers.ValidationError("Reference ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Reference ID does not exist.")

        return super().validate(data)

    def create(self, validated_data):
        ref_id = self.initial_data.get("reference_id")
        reference = Reference.objects.get(id=ref_id)
        if models.Study.objects.filter(reference_ptr=ref_id).exists():
            raise serializers.ValidationError(f"Reference ID {ref_id} already linked with a study.")
        if not reference.assessment.user_can_edit_object(self.context["request"].user):
            raise exceptions.PermissionDenied("Invalid permission to edit assessment.")
        validated_data["assessment"] = reference.assessment.id

        return models.Study.save_new_from_reference(reference, validated_data)

    class Meta:
        model = models.Study
        exclude = (
            "searches",
            "identifiers",
        )
        extra_kwargs = {
            "assessment": {"required": False},
            "full_citation": {"required": False},
            "short_citation": {"required": False},
        }


class StudyAssessmentSerializer(serializers.ModelSerializer):
    assessment = AssessmentMiniSerializer(read_only=True)
    url = serializers.CharField(source="get_absolute_url")

    class Meta:
        model = models.Study
        fields = ("id", "url", "assessment", "short_citation")


class VerboseStudySerializer(StudySerializer):
    assessment = AssessmentMiniSerializer(read_only=True)
    searches = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    riskofbiases = RiskOfBiasSerializer(many=True, read_only=True)
    rob_settings = AssessmentRiskOfBiasSerializer(source="assessment")
    identifiers = IdentifiersSerializer(many=True)
    tags = ReferenceTagsSerializer()

    class Meta:
        model = models.Study
        fields = "__all__"


class StudyCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Study
        cleanup_fields = model.TEXT_CLEANUP_FIELDS
        fields = ("id", "short_citation",) + cleanup_fields


SerializerHelper.add_serializer(models.Study, VerboseStudySerializer)
