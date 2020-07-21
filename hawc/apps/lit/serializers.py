import logging
from io import StringIO
from typing import List

import django.core.exceptions
import pandas as pd
from celery import chain
from django.db import transaction
from django.template.defaultfilters import slugify
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ParseError

from ..assessment.serializers import AssessmentRootedSerializer
from ..common.api import DynamicFieldsMixin
from . import constants, forms, models, tasks


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
            raise serializers.ValidationError(
                f"Invalid column headers; expecting \"{','.join(expected_columns)}\""
            )

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
            raise serializers.ValidationError(
                f"All reference ids are not from assessment {expected_assessment_id}"
            )

        # ensure that all tags are from this assessment
        expected_tag_ids = models.ReferenceFilterTag.get_descendants_pks(expected_assessment_id)
        additional_tags = set(df.tag_id.unique()) - set(expected_tag_ids)
        if len(additional_tags) > 0:
            raise serializers.ValidationError(
                f"All tag ids are not from assessment {expected_assessment_id}"
            )

        # check to make sure we have no duplicates
        df_nrows = df.shape[0]
        df = df.drop_duplicates()
        if df.shape[0] != df_nrows:
            raise serializers.ValidationError(
                "CSV contained duplicates; please remove before importing"
            )

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
                models.ReferenceTags.objects.filter(
                    content_object__assessment_id=assessment_id
                ).values_list("tag_id", "content_object_id")
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

    def validate_tags(self, value):
        valid_tags = models.ReferenceFilterTag.get_assessment_qs(
            self.instance.assessment_id
        ).filter(id__in=value)
        if valid_tags.count() != len(value):
            raise serializers.ValidationError(f"All tag ids are not from this assessment")
        return value

    @transaction.atomic()
    def update(self, instance, validated_data):

        # updates the reference tags
        if "tags" in validated_data:
            instance.tags.set(validated_data.pop("tags"))
        # updates the rest of the fields
        for attr, value in list(validated_data.items()):
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = models.Reference
        fields = "__all__"


class ReferenceReplaceListSerializer(serializers.ListSerializer):
    def validate_context(self):

        # 'replace' should be in our context
        if "replace" not in self.context:
            raise serializers.ValidationError(
                f"Must pass context 'replace':[[reference_id,hero_id],...]"
            )

        # unzip 'replace' and save it to our serializer
        # the values are needed below and in our 'execute' method
        replace = self.context.get("replace")
        self.ref_ids, self.hero_ids = list(zip(*replace))

        # make sure all references are in the queryset
        matching_references = self.instance.filter(id__in=self.ref_ids)
        if matching_references.count() != len(self.ref_ids):
            raise serializers.ValidationError("All references must be from selected assessment.")

        # make sure updated references will have unique HERO IDs
        references_diff = self.instance.difference(matching_references).values_list("id", flat=True)
        identifiers_diff = models.Identifiers.objects.filter(
            references__in=references_diff, database=constants.HERO
        )
        hero_diff = identifiers_diff.values_list("unique_id", flat=True)
        hero_all = list(hero_diff) + list(self.hero_ids)

        # are there duplice HERO references?
        if len(hero_all) > len(set(hero_all)):
            raise serializers.ValidationError("Duplicate HERO references.")

        # make sure all HERO IDs are valid
        try:
            _, _, self.fetched_content = models.Identifiers.objects.validate_valid_hero_ids(
                self.hero_ids
            )
        except django.core.exceptions.ValidationError as err:
            raise serializers.ValidationError(err.args[0])

    def execute(self):
        self.validate_context()

        replace = self.context.get("replace")

        # import missing identifers
        models.Identifiers.objects.bulk_create_hero_ids(self.fetched_content)
        # set hero ref
        t1 = tasks.replace_hero_ids.si(replace)
        # update content
        t2 = tasks.update_hero_content.si(self.hero_ids)
        # update fields with content
        t3 = tasks.update_hero_fields.si(self.ref_ids)

        # run chained tasks
        return chain(t1, t2, t3)()


class ReferenceReplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reference
        list_serializer_class = ReferenceReplaceListSerializer
        fields = "__all__"


class ReferenceUpdateListSerializer(serializers.ListSerializer):
    def execute(self):

        ref_ids = set(self.instance.values_list("id", flat=True))
        identifiers = models.Identifiers.objects.filter(
            references__in=ref_ids, database=constants.HERO
        )
        hero_ids = identifiers.values_list("unique_id", flat=True)

        # update content of hero identifiers
        t1 = tasks.update_hero_content.si(hero_ids)
        # update fields from content
        t2 = tasks.update_hero_fields.si(ref_ids)

        # run chained tasks
        return chain(t1, t2)()


class ReferenceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reference
        list_serializer_class = ReferenceUpdateListSerializer
        fields = "__all__"
