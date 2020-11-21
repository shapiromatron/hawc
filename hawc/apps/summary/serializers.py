import json
from django.core.exceptions import ValidationError

from rest_framework import serializers

from ..common.helper import SerializerHelper
from . import models


class CollectionDataPivotSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        ret["visual_type"] = instance.visual_type
        return ret

    class Meta:
        model = models.DataPivot
        exclude = ("settings",)


class DataPivotSerializer(CollectionDataPivotSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["settings"] = instance.get_settings()
        ret["data_url"] = instance.get_data_url()
        ret["download_url"] = instance.get_download_url()
        return ret


class CollectionVisualSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["url"] = instance.get_absolute_url()
        ret["visual_type"] = instance.get_rob_visual_type_display(
            instance.get_visual_type_display()
        )
        try:
            settings = json.loads(instance.settings)
        except json.JSONDecodeError:
            settings = {}
        ret["settings"] = settings
        return ret

    class Meta:
        model = models.Visual
        exclude = (
            "endpoints",
            "studies",
        )


class VisualSerializer(CollectionVisualSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret["url_update"] = instance.get_update_url()
        ret["url_delete"] = instance.get_delete_url()

        ret["endpoints"] = [
            SerializerHelper.get_serialized(d, json=False) for d in instance.get_endpoints()
        ]

        ret["studies"] = [
            SerializerHelper.get_serialized(d, json=False) for d in instance.get_studies()
        ]

        ret["assessment_rob_name"] = instance.assessment.get_rob_name_display()

        return ret


class SummaryTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SummaryText
        fields = "__all__"

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        if parent is not None and parent.assessment != self.instance.assessment:
            raise ValidationError("Parent must be from the same assessment")
        return parent

    def clean_sibling(self):
        sibling = self.cleaned_data.get("sibling")
        if sibling is not None and sibling.assessment != self.instance.assessment:
            raise ValidationError("Sibling must be from the same assessment")
        return sibling

    def clean_title(self):
        title = self.cleaned_data["title"]
        pk_exclusion = {"id": self.instance.id or -1}
        if (
            models.SummaryText.objects.filter(assessment=self.instance.assessment, title=title)
            .exclude(**pk_exclusion)
            .count()
            > 0
        ):
            raise ValidationError("Title must be unique for assessment.")
        return title

    def clean_slug(self):
        slug = self.cleaned_data["slug"]
        pk_exclusion = {"id": self.instance.id or -1}
        if (
            models.SummaryText.objects.filter(assessment=self.instance.assessment, slug=slug)
            .exclude(**pk_exclusion)
            .count()
            > 0
        ):
            raise ValidationError("Slug must be unique for assessment.")
        return slug

    def create(cls, form):
        # todo - move to serializer
        instance = form.save(commit=False)
        sibling = form.cleaned_data.get("sibling")
        if sibling:
            return sibling.add_sibling(pos="right", instance=instance)
        else:
            parent = form.cleaned_data.get(
                "parent", SummaryText.get_assessment_root_node(instance.assessment.id)
            )
            sibling = parent.get_first_child()
            if sibling:
                return sibling.add_sibling(pos="first-sibling", instance=instance)
            else:
                return parent.add_child(instance=instance)

    def update(self, form):
        # todo move to serializer
        data = form.cleaned_data

        parent = data.get("parent")
        sibling = data.get("sibling")
        if parent is not None and parent.assessment != self.assessment:
            raise ValueError("Parent assessment != self assessment")

        if sibling is not None and sibling.assessment != self.assessment:
            raise ValueError("Sibling assessment != self assessment")

        if sibling:
            if self.get_prev_sibling() != sibling:
                self.move(sibling, pos="right")
        elif parent:
            self.move(parent, pos="first-child")

        self.title = data["title"]
        self.slug = data["slug"]
        self.text = data["text"]
        self.save()


SerializerHelper.add_serializer(models.Visual, VisualSerializer)
