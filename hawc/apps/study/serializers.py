from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import exceptions, serializers

from ..assessment.models import Assessment
from ..assessment.serializers import AssessmentMiniSerializer
from ..common.api import DynamicFieldsMixin
from ..common.helper import SerializerHelper
from ..common.serializers import IdLookupMixin
from ..lit.constants import DOI_EXACT, DOI_EXAMPLE, ReferenceDatabase
from ..lit.models import Identifiers, Reference
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


class SimpleStudySerializer(StudySerializer):
    def validate(self, data):
        if "reference_id" in self.initial_data:

            ref_id = self.initial_data.get("reference_id")

            try:
                Reference.objects.get(id=ref_id)
            except ValueError:
                raise serializers.ValidationError("Reference ID must be a number.")
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Reference ID does not exist.")

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
    riskofbiases = serializers.SerializerMethodField()
    rob_settings = AssessmentRiskOfBiasSerializer(source="assessment")
    identifiers = IdentifiersSerializer(many=True)
    tags = ReferenceTagsSerializer()

    def get_riskofbiases(self, study):
        return FinalRiskOfBiasSerializer(study.get_final_qs(), many=True).data

    class Meta:
        model = models.Study
        fields = "__all__"


class StudyFromIdentifierSerializer(serializers.ModelSerializer):
    db_type = serializers.ChoiceField(choices=["PUBMED", "HERO", "DOI"], write_only=True)
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
                f"Study for this assessment and identifier already exists (study {study.id})"
            )
        # if identifier does not exist, it must be validated
        data["identifier"] = Identifiers.objects.filter(
            database=data["db_type"], unique_id=str(data["db_id"])
        ).first()
        if data["identifier"] is None:
            try:
                if data["db_type"] == ReferenceDatabase.PUBMED:
                    _, _, self._identifier_content = Identifiers.objects.validate_pubmed_ids(
                        [int(data["db_id"])]
                    )
                elif data["db_type"] == ReferenceDatabase.HERO:
                    _, _, self._identifier_content = Identifiers.objects.validate_valid_hero_ids(
                        [int(data["db_id"])]
                    )
                elif data["db_type"] == ReferenceDatabase.DOI:
                    if not DOI_EXACT.fullmatch(data["db_id"]):
                        raise Exception(f'Invalid DOI; should be in format "{DOI_EXAMPLE}"')
            except Exception:
                raise serializers.ValidationError(
                    f'Unable to import {data["db_type"].label} ID {data["db_id"]}.'
                )
        return data

    @transaction.atomic
    def create(self, validated_data):
        assessment = validated_data.pop("assessment")
        db_type = validated_data.pop("db_type")
        db_id = validated_data.pop("db_id")

        if (ident := validated_data.pop("identifier")) is None:
            if db_type == ReferenceDatabase.PUBMED:
                ident = Identifiers.objects.bulk_create_pubmed_ids(self._identifier_content)[0]
            elif db_type == ReferenceDatabase.HERO:
                ident = Identifiers.objects.bulk_create_hero_ids(self._identifier_content)[0]
            elif db_type == ReferenceDatabase.DOI:
                ident = Identifiers.objects.create(database=db_type, unique_id=db_id)

        if (
            ref := Reference.objects.filter(assessment=assessment, identifiers=ident).first()
        ) is None:
            ref = ident.create_reference(assessment)
            ref.save()
            ref.identifiers.add(ident)

        return models.Study.save_new_from_reference(ref, validated_data)

    class Meta:
        model = models.Study
        exclude = (
            "assessment",
            "searches",
            "identifiers",
        )
        extra_kwargs = {
            "full_citation": {"required": False},
            "short_citation": {"required": False},
        }


class StudyCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Study
        cleanup_fields = model.TEXT_CLEANUP_FIELDS
        fields = ("id", "short_citation",) + cleanup_fields


SerializerHelper.add_serializer(models.Study, VerboseStudySerializer)
