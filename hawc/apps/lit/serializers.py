import logging
from io import StringIO
from typing import List

import pandas as pd
from django.db import transaction
from django.template.defaultfilters import slugify
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ParseError

from ..assessment.serializers import AssessmentRootedSerializer
from ..common.api import DynamicFieldsMixin
from . import constants, forms, models


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Search
        fields = (
            "assessment",
            "search_type",
            "source",
            "title",
            "slug",
            "description",
            "search_string",
            "created",
            "last_updated",
        )
        read_only_fields = ["slug", "created", "last_updated"]

    def validate(self, data):

        user = self.context["request"].user
        if not data["assessment"].user_can_edit_object(user):
            # TODO - move authentication check outside validation?
            raise exceptions.PermissionDenied("Invalid permissions to edit assessment")

        if data["search_type"] != "i":
            raise serializers.ValidationError("API currently only supports imports")

        if data["source"] != constants.HERO:
            raise serializers.ValidationError("API currently only supports HERO imports")

        if data["search_type"] == "i":
            ids = forms.ImportForm.validate_import_search_string(data["search_string"])
            self.validate_import_ids_exist(data, ids)

        return data

    def validate_import_ids_exist(self, data, ids: List[int]):
        if data["source"] == constants.HERO:
            _, _, content = models.Identifiers.objects.validate_valid_hero_ids(ids)
            self._import_data = dict(ids=ids, content=content)
        else:
            raise NotImplementedError()

    @transaction.atomic
    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["title"])
        # create search object
        search = models.Search.objects.create(**validated_data)
        # create missing identifiers from import
        models.Identifiers.objects.bulk_create_hero_ids(self._import_data["content"])
        # get hero identifiers
        identifiers = models.Identifiers.objects.hero(self._import_data["ids"])
        # get or create  reference objects from identifiers
        models.Reference.objects.get_hero_references(search, identifiers)
        return search


class IdentifiersSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["database"] = instance.get_database_display()
        ret["url"] = instance.get_url()
        return ret

    class Meta:
        model = models.Identifiers
        fields = "__all__"


class ReferenceTagsSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        raise ParseError("Not implemented!")

    def to_representation(self, obj):
        # obj is a model-manager in this case; convert to list to serialize
        return list(obj.values("id", "name"))

    class Meta:
        model = models.ReferenceTags
        fields = "__all__"


class ReferenceFilterTagSerializer(AssessmentRootedSerializer):
    parent = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = models.ReferenceFilterTag
        fields = ("id", "name", "parent")


class ReferenceCleanupFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Reference
        cleanup_fields = model.TEXT_CLEANUP_FIELDS
        fields = cleanup_fields + ("id",)


class BulkReferenceTagSerializer(serializers.Serializer):
    operation = serializers.ChoiceField(choices=["append", "replace"], required=True)
    csv = serializers.CharField(required=True)

    def validate_csv(self, value):
        try:
            df = pd.read_csv(StringIO(value))
        except pd.errors.ParserError:
            raise serializers.ValidationError("CSV could not be parsed")
        except pd.errors.EmptyDataError:
            raise serializers.ValidationError("CSV must not be empty")

        # ensure columns are expected
        expected_columns = ["reference_id", "tag_id"]
        if df.columns.tolist() != expected_columns:
            raise serializers.ValidationError(f"Invalid column headers; expecting \"{','.join(expected_columns)}\"")

        # ensure we have some data
        if df.shape[0] == 0:
            raise serializers.ValidationError("CSV has no data")

        expected_assessment_id = self.context["assessment"].id

        # ensure that all references are from this assessment
        assessments = (
            models.Reference.objects.filter(id__in=df.reference_id.unique())
            .values_list("assessment_id", flat=True)
            .distinct()
        )
        if len(assessments) != 1 or assessments[0] != expected_assessment_id:
            raise serializers.ValidationError(f"All reference ids are not from assessment {expected_assessment_id}")

        # ensure that all tags are from this assessment
        expected_tag_ids = models.ReferenceFilterTag.get_descendants_pks(expected_assessment_id)
        additional_tags = set(df.tag_id.unique()) - set(expected_tag_ids)
        if len(additional_tags) > 0:
            raise serializers.ValidationError(f"All tag ids are not from assessment {expected_assessment_id}")

        # check to make sure we have no duplicates
        df_nrows = df.shape[0]
        df = df.drop_duplicates()
        if df.shape[0] != df_nrows:
            raise serializers.ValidationError("CSV contained duplicates; please remove before importing")

        # success! save dataframe
        self.assessment = self.context["assessment"]
        self.df = df

        return value

    @transaction.atomic
    def bulk_create_tags(self):
        assessment_id = self.assessment.id
        operation = self.validated_data["operation"]

        existing = set()
        if operation == "append":
            existing = set(
                models.ReferenceTags.objects.filter(content_object__assessment_id=assessment_id).values_list(
                    "tag_id", "content_object_id"
                )
            )

        if operation == "replace":
            tags_to_delete = models.ReferenceTags.objects.assessment_qs(assessment_id)
            logging.info(f"Deleting {tags_to_delete.count()} reference tags for {assessment_id}")
            tags_to_delete.delete()

        new_tags = [
            models.ReferenceTags(tag_id=row.tag_id, content_object_id=row.reference_id)
            for row in self.df.itertuples(index=False)
            if (row.tag_id, row.reference_id) not in existing
        ]

        if new_tags:
            logging.info(f"Creating {len(new_tags)} reference tags for {assessment_id}")
            models.ReferenceTags.objects.bulk_create(new_tags)

            models.Reference.delete_cache(assessment_id)


class ReferenceSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(write_only=True)

    def update(self, instance, validated_data):

        instance.title = validated_data.get("title", instance.title)
        if "tags" in validated_data:
            instance.tags.set(validated_data.get("tags"))

        instance.save()
        return instance

    class Meta:
        model = models.Reference
        fields = "__all__"
