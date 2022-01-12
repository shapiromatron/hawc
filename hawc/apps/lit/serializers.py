import itertools
import logging
from collections import Counter
from io import StringIO
from typing import List

import django.core.exceptions
import pandas as pd
from celery import chain
from celery.result import ResultBase
from django.db import transaction
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.urls import reverse
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ParseError

from ..assessment.serializers import AssessmentRootedSerializer
from ..common.api import DynamicFieldsMixin
from ..common.forms import ASSESSMENT_UNIQUE_MESSAGE
from ..common.serializers import validate_jsonschema
from . import constants, exports, forms, models, tasks

logger = logging.getLogger(__name__)


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

        # set slug value based on title; assert it's unique
        # (assessment+title is checked w/ built-in serializer)
        data["slug"] = slugify(data["title"])
        if models.Search.objects.filter(assessment=data["assessment"], slug=data["slug"]).exists():
            raise serializers.ValidationError({"slug": ASSESSMENT_UNIQUE_MESSAGE})

        if data["search_type"] != constants.SearchType.IMPORT:
            raise serializers.ValidationError("API currently only supports imports")

        if data["source"] != constants.ReferenceDatabase.HERO:
            raise serializers.ValidationError("API currently only supports HERO imports")

        if data["search_type"] == constants.SearchType.IMPORT:
            ids = forms.ImportForm.validate_import_search_string(data["search_string"])
            self.validate_import_ids_exist(data, ids)

        return data

    def validate_import_ids_exist(self, data, ids: List[int]):
        if data["source"] == constants.ReferenceDatabase.HERO:
            _, _, content = models.Identifiers.objects.validate_valid_hero_ids(ids)
            self._import_data = dict(ids=ids, content=content)
        else:
            raise NotImplementedError()

    @transaction.atomic
    def create(self, validated_data):
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


class ReferenceQuerySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    db_id = serializers.CharField(required=False, allow_blank=True)
    year = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(required=False, allow_blank=True)
    authors = serializers.CharField(required=False, allow_blank=True)
    journal = serializers.CharField(required=False, allow_blank=True)
    abstract = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
        required=False,
        min_length=0,
        max_length=10,
    )

    def validate_tags(self, values):
        assessment = self.context["assessment"]
        if len(values) > 0:
            try:
                self._tags = models.ReferenceFilterTag.get_tags_in_assessment(assessment.id, values)
            except ValueError:
                raise serializers.ValidationError("Invalid tag IDs")
        return values

    def search(self):
        qs = models.Reference.objects.filter(assessment=self.context["assessment"])
        query = Q()
        if "id" in self.data and self.data["id"] is not None:
            query &= Q(id=self.data["id"])
        if db_id := self.data.get("db_id", ""):
            query &= Q(identifiers__unique_id__icontains=db_id)
        if "year" in self.data and self.data["year"] is not None:
            query &= Q(year=self.data["year"])
        if "title" in self.data:
            query &= Q(title__icontains=self.data["title"])
        if "authors" in self.data:
            query &= Q(authors_short__unaccent__icontains=self.data["authors"]) | Q(
                authors__unaccent__icontains=self.data["authors"]
            )
        if "journal" in self.data:
            query &= Q(journal__icontains=self.data["journal"])
        if "abstract" in self.data:
            query &= Q(abstract__icontains=self.data["abstract"])
        if tags := getattr(self, "_tags", None):
            # don't use a Q for tags; Q creates a subquery with join instead; this approach
            # appends additional where clauses which are much more performant
            for tag in tags:
                tag_ids = list(tag.get_tree(parent=tag).values_list("id", flat=True))
                qs = qs.filter(tags__in=tag_ids)
        qs = (
            qs.filter(query)
            .select_related("study")
            .prefetch_related("searches", "identifiers")[:100]
        )
        return [ref.to_dict() for ref in qs]


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


class ReferenceTreeSerializer(serializers.Serializer):
    tree = serializers.JSONField()

    tree_schema = {
        "$id": "tree",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$defs": {
            "tagNode": {
                "type": "object",
                "additionalProperties": False,
                "required": ["data"],
                "properties": {
                    "id": {"type": "integer"},
                    "data": {
                        "type": "object",
                        "required": ["name"],
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string", "minLength": 1, "maxLength": 128},
                            "slug": {"type": "string", "pattern": r"^[-a-zA-Z0-9_]+$"},
                        },
                    },
                    "children": {"type": "array", "items": {"$ref": "#/$defs/tagNode"}},
                },
            }
        },
        "type": "array",
        "items": {"$ref": "#/$defs/tagNode"},
    }

    def validate_tree(self, value):
        return validate_jsonschema(value, self.tree_schema)

    def update(self):
        assessment_id = self.context["assessment"].id
        models.ReferenceFilterTag.replace_tree(assessment_id, self.validated_data["tree"])

    def to_representation(self, instance):
        assessment_id = self.context["assessment"].id
        root = models.ReferenceFilterTag.get_assessment_root(assessment_id)
        tree = root.dump_bulk(root, keep_ids=True)
        return {"tree": tree[0].get("children", [])}


class BulkReferenceTagSerializer(serializers.Serializer):
    operation = serializers.ChoiceField(choices=["append", "replace", "remove"], required=True)
    csv = serializers.CharField(required=True)
    dry_run = serializers.BooleanField(default=False)

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
        unique_refs = df.reference_id.unique()

        # ensure that all references are from this assessment
        assessments = (
            models.Reference.objects.filter(id__in=unique_refs)
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

        # ensure all references exist
        founds_refs = set(
            models.Reference.objects.filter(id__in=unique_refs).values_list("id", flat=True)
        )
        missing = set(unique_refs) - set(founds_refs)
        if missing:
            raise serializers.ValidationError(f"Reference(s) not found: {missing}")

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
        if self.validated_data["dry_run"]:
            return

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
            qs = models.ReferenceTags.objects.assessment_qs(assessment_id)
            logger.info(f"Deleting {qs.count()} reference tags for {assessment_id}")
            qs.delete()

        if operation == "remove":
            query = Q()
            for row in self.df.itertuples(index=False):
                query |= Q(tag_id=row.tag_id, content_object_id=row.reference_id)
            qs = models.ReferenceTags.objects.assessment_qs(assessment_id).filter(query)
            logger.info(f"Deleting {qs.count()} reference tags for {assessment_id}")
            qs.delete()
            return

        new_tags = [
            models.ReferenceTags(tag_id=row.tag_id, content_object_id=row.reference_id)
            for row in self.df.itertuples(index=False)
            if (row.tag_id, row.reference_id) not in existing
        ]

        if new_tags:
            logger.info(f"Creating {len(new_tags)} reference tags for {assessment_id}")
            models.ReferenceTags.objects.bulk_create(new_tags)
            models.Reference.delete_cache(assessment_id)


class ReferenceSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(write_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["pk"] = instance.id
        ret["assessment_id"] = instance.assessment_id

        ret["has_study"] = instance.has_study
        ret["url"] = instance.get_absolute_url()
        ret["editTagUrl"] = reverse("lit:reference_tags_edit", kwargs={"pk": instance.pk})
        ret["editReferenceUrl"] = reverse("lit:ref_edit", kwargs={"pk": instance.pk})
        ret["deleteReferenceUrl"] = reverse("lit:ref_delete", kwargs={"pk": instance.pk})

        ret["identifiers"] = [ident.to_dict() for ident in instance.identifiers.all()]
        ret["searches"] = [search.to_dict() for search in instance.searches.all()]
        ret["study_short_citation"] = instance.study.short_citation if ret["has_study"] else None

        ret["tags"] = [tag.id for tag in instance.tags.all()]
        return ret

    def validate_tags(self, value):
        valid_tags = models.ReferenceFilterTag.get_assessment_qs(
            self.instance.assessment_id
        ).filter(id__in=value)
        if valid_tags.count() != len(value):
            raise serializers.ValidationError("All tag ids are not from this assessment")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):

        # updates the reference tags
        if "tags" in validated_data:
            instance.tags.set(validated_data.pop("tags"))
        # updates the searches
        if "searches" in validated_data:
            instance.searches.set(validated_data.pop("searches"))
        # updates the rest of the fields
        for attr, value in list(validated_data.items()):
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = models.Reference
        fields = "__all__"


class ReferenceReplaceHeroIdSerializer(serializers.Serializer):
    replace = serializers.ListField(
        min_length=1,
        max_length=1000,
        child=serializers.ListField(min_length=2, max_length=2, child=serializers.IntegerField()),
    )

    def validate_replace(self, replace: List) -> List:

        self.ref_ids, self.hero_ids = zip(*replace)
        assessment = self.context["assessment"]
        references = models.Reference.objects.filter(id__in=self.ref_ids)

        # make sure references exist
        if references.count() != len(self.ref_ids):
            raise serializers.ValidationError("All references not found; check ID list")

        # make sure references are part of the assessment
        ref_assessment_ids = set(ref.assessment_id for ref in references)
        if len(ref_assessment_ids) != 1:
            raise serializers.ValidationError(
                f"Reference IDs from multiple assessments: {ref_assessment_ids}"
            )

        if list(ref_assessment_ids)[0] != assessment.id:
            raise serializers.ValidationError(
                f"Reference IDs not all from assessment {assessment.id}."
            )

        # make sure HERO IDs are unique for all references in an assessment

        # get hero ids for unmodified references
        references_diff = (
            models.Reference.objects.hero_references(assessment.id)
            .difference(references)
            .values_list("id", flat=True)
        )
        existing_hero_ids = [
            int(id_)
            for id_ in models.Identifiers.objects.filter(
                references__in=references_diff, database=constants.ReferenceDatabase.HERO
            ).values_list("unique_id", flat=True)
        ]
        hero_counts = Counter(itertools.chain(existing_hero_ids, self.hero_ids))
        duplicates = [key for key, count in hero_counts.items() if count > 1]
        if len(duplicates) > 0:
            raise serializers.ValidationError(
                f"Duplicate HERO IDs in assessment: {list(duplicates)}"
            )

        # make sure all HERO IDs are valid; and save response from HERO if needed
        try:
            _, _, self.fetched_content = models.Identifiers.objects.validate_valid_hero_ids(
                self.hero_ids
            )
        except django.core.exceptions.ValidationError as err:
            raise serializers.ValidationError(err.args[0])

        return replace

    def execute(self) -> ResultBase:

        # import missing identifers
        models.Identifiers.objects.bulk_create_hero_ids(self.fetched_content)

        # set hero ref
        t1 = tasks.replace_hero_ids.si(self.validated_data["replace"])

        # update content
        t2 = tasks.update_hero_content.si(self.hero_ids)

        # update fields with content
        t3 = tasks.update_hero_fields.si(self.ref_ids)

        # run chained tasks
        return chain(t1, t2, t3)()


class ReferenceTagExportSerializer(serializers.Serializer):
    nested = serializers.ChoiceField(choices=[("t", "true"), ("f", "false")], default="t")
    exporter = serializers.ChoiceField(
        choices=[("base", "base"), ("table-builder", "table builder")], default="base"
    )
    _exporters = {
        "base": exports.ReferenceFlatComplete,
        "table-builder": exports.TableBuilderFormat,
    }

    def get_exporter(self):
        return self._exporters[self.validated_data["exporter"]]

    def include_descendants(self):
        return self.validated_data["nested"] == "t"
