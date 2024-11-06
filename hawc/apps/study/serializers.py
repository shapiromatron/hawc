from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers

from ..assessment.models import Assessment
from ..assessment.serializers import AssessmentMiniSerializer
from ..common.api import DynamicFieldsMixin
from ..common.helper import SerializerHelper
from ..common.serializers import IdLookupMixin
from ..lit.constants import ReferenceDatabase
from ..lit.forms import create_external_id, validate_external_id
from ..lit.models import Reference
from ..lit.serializers import IdentifiersSerializer, ReferenceTagsSerializer
from ..riskofbias.serializers import AssessmentRiskOfBiasSerializer, FinalRiskOfBiasSerializer
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
        read_only_fields = ("identifiers", "searches")


class SimpleStudySerializer(StudySerializer):
    def validate(self, data):
        if "reference_id" in self.initial_data:
            ref_id = self.initial_data.get("reference_id")

            try:
                Reference.objects.get(id=ref_id)
            except ValueError as err:
                raise serializers.ValidationError("Reference ID must be a number.") from err
            except ObjectDoesNotExist as err:
                raise serializers.ValidationError("Reference ID does not exist.") from err

        return super().validate(data)

    def create(self, validated_data):
        ref_id = self.initial_data.get("reference_id")
        reference = get_object_or_404(Reference, id=ref_id)
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
    riskofbiases = serializers.SerializerMethodField()
    rob_settings = AssessmentRiskOfBiasSerializer(source="assessment")
    identifiers = IdentifiersSerializer(many=True)
    tags = ReferenceTagsSerializer()

    def _get_identifier(self, identifiers: list, key: str, to_int: bool) -> int | str | None:
        for identifier in identifiers:
            if identifier["database"] == key:
                value = identifier["unique_id"]
                return int(value) if to_int else value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["hero_id"] = self._get_identifier(ret["identifiers"], "HERO", True)
        ret["pubmed_id"] = self._get_identifier(ret["identifiers"], "PubMed", True)
        ret["doi"] = self._get_identifier(ret["identifiers"], "DOI", False)
        return ret

    def get_riskofbiases(self, study):
        return FinalRiskOfBiasSerializer(study.get_final_qs(), many=True).data

    class Meta:
        model = models.Study
        fields = "__all__"


class StudyFromIdentifierSerializer(serializers.ModelSerializer):
    db_type = serializers.ChoiceField(choices=["PUBMED", "HERO"], write_only=True)
    db_id = serializers.CharField(write_only=True)
    assessment_id = serializers.PrimaryKeyRelatedField(
        queryset=Assessment.objects.all(), source="assessment"
    )

    def validate(self, data):
        data["db_type"] = ReferenceDatabase[data["db_type"]]
        # study should be creatable; ie. does not exist
        if (
            study := models.Study.objects.filter(
                assessment_id=data["assessment"],
                identifiers__database=data["db_type"],
                identifiers__unique_id=str(data["db_id"]),
            ).first()
        ) is not None:
            raise serializers.ValidationError(
                {"db_id": f"Study already exists; see {study} [{study.id}]"}
            )
        # validate identifier
        try:
            data["identifier"], self._identifier_content = validate_external_id(
                data["db_type"], data["db_id"]
            )
        except ValidationError as err:
            raise serializers.ValidationError(err.message) from err

        return data

    @transaction.atomic
    def create(self, validated_data):
        assessment = validated_data.pop("assessment")
        db_type = validated_data.pop("db_type")
        validated_data.pop("db_id")

        if (ident := validated_data.pop("identifier")) is None:
            ident = create_external_id(db_type, self._identifier_content)

        if (
            ref := Reference.objects.filter(assessment=assessment, identifiers=ident).first()
        ) is None:
            ref = ident.create_reference(assessment)
            ref.save()
            ref.identifiers.add(ident)

        return models.Study.save_new_from_reference(ref, validated_data)

    class Meta:
        model = models.Study
        exclude = ("assessment", "searches", "identifiers")
        extra_kwargs = {
            "full_citation": {"required": False},
            "short_citation": {"required": False},
        }


class StudyCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Study
        cleanup_fields = model.TEXT_CLEANUP_FIELDS
        fields = ("id", "short_citation", *cleanup_fields)


SerializerHelper.add_serializer(models.Study, VerboseStudySerializer)


class GlobalStudySerializer(serializers.ModelSerializer):
    assessment_creator = serializers.EmailField(source="assessment.creator.email")
    assessment_name = serializers.CharField(source="assessment.name")
    assessment_status = serializers.CharField()

    class Meta:
        model = models.Study
        fields = [
            "id",
            "title",
            "short_citation",
            "published",
            "assessment_id",
            "assessment_name",
            "assessment_creator",
            "assessment_status",
        ]
