import django_filters as df
from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef, Prefetch, Q

from ..assessment.autocomplete import LabelAutocomplete
from ..assessment.constants import RobName
from ..assessment.models import LabeledItem
from ..common.filterset import (
    AutocompleteModelMultipleChoiceFilter,
    BaseFilterSet,
    InlineFilterForm,
)
from . import constants, models


class VisualFilterSet(BaseFilterSet):
    title = df.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Title text",
        help_text="Filter by title",
    )
    type = df.ChoiceFilter(
        field_name="visual_type",
        label="Visualization type",
        help_text="Type of visualization to display",
        empty_label="All visual types",
    )
    label = AutocompleteModelMultipleChoiceFilter(
        autocomplete_class=LabelAutocomplete,
        method="filter_labels",
    )
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC visualization",
        empty_label="Published status",
    )

    class Meta:
        model = models.Visual
        fields = ["title", "type", "label", "published"]
        form = InlineFilterForm

    def annotate_queryset(self, queryset):
        query = Q()
        if not self.perms["edit"]:
            query &= Q(label__published=True)
        return queryset.prefetch_related(
            Prefetch(
                "labels",
                queryset=LabeledItem.objects.filter(query).select_related("label"),
                to_attr="visible_labels",
            )
        )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = self.annotate_queryset(queryset)
        query = Q(assessment=self.assessment)
        if not self.perms["edit"]:
            query &= Q(published=True)
        return queryset.filter(query).order_by("id")

    def filter_labels(self, queryset, name, value):
        if not value:
            return queryset
        content_type = ContentType.objects.get_for_model(models.Visual)
        for label in value:
            subquery = LabeledItem.objects.filter(
                **(dict(label__published=True) if not self.perms["edit"] else dict()),
                label__path__startswith=label.path,
                label__depth__gte=label.depth,
                content_type=content_type,
                object_id=OuterRef("pk"),
            )
            queryset = queryset.filter(Exists(subquery))
        return queryset

    def get_type_choices(self):
        choices = (
            models.Visual.objects.filter(assessment=self.assessment)
            .values_list("visual_type", flat=True)
            .distinct()
        )
        choices = [constants.VisualType(choice) for choice in sorted(set(choices))]

        choices = [(choice.value, choice.label) for choice in choices]
        if self.assessment.rob_name == RobName.SE:
            choices = [
                (value, label.replace("risk of bias", "study evaluation"))
                for value, label in choices
            ]
        return choices

    def create_form(self):
        form = super().create_form()
        form.fields["type"].choices = self.get_type_choices()
        form.fields["label"].set_filters(
            {"assessment_id": self.assessment.id, "published": True}
            if not self.perms["edit"]
            else {"assessment_id": self.assessment.id}
        )
        form.fields["label"].widget.attrs.update({"data-placeholder": "Labels"})
        form.fields["label"].widget.attrs["size"] = 1
        return form


class SummaryTableFilterSet(BaseFilterSet):
    title = df.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Title",
        help_text="Filter by title",
    )
    type = df.ChoiceFilter(
        field_name="table_type",
        label="Table type",
        help_text="Type of summary table to display",
        empty_label="All table types",
    )
    label = AutocompleteModelMultipleChoiceFilter(
        autocomplete_class=LabelAutocomplete,
        method="filter_labels",
    )
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC summary tables",
        empty_label="Published status",
    )

    class Meta:
        model = models.SummaryTable
        fields = ["title", "type", "label", "published"]
        form = InlineFilterForm

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        query = Q(assessment=self.assessment)
        label_query = Q()
        if not self.perms["edit"]:
            label_query &= Q(label__published=True)
            query &= Q(published=True)
        return (
            queryset.filter(query)
            .prefetch_related(
                Prefetch(
                    "labels",
                    queryset=LabeledItem.objects.filter(label_query).select_related("label"),
                    to_attr="visible_labels",
                )
            )
            .order_by("id")
        )

    def filter_labels(self, queryset, name, value):
        if not value:
            return queryset
        content_type = ContentType.objects.get_for_model(models.SummaryTable)
        for label in value:
            subquery = LabeledItem.objects.filter(
                **(dict(label__published=True) if not self.perms["edit"] else dict()),
                label__path__startswith=label.path,
                label__depth__gte=label.depth,
                content_type=content_type,
                object_id=OuterRef("pk"),
            )
            queryset = queryset.filter(Exists(subquery))
        return queryset

    def create_form(self):
        form = super().create_form()

        # set type choices based on what is available
        choices = models.SummaryTable.objects.filter(assessment=self.assessment).values_list(
            "table_type", flat=True
        )
        choices = [constants.TableType(choice) for choice in sorted(set(choices))]
        form.fields["type"].choices = [(choice.value, choice.label) for choice in choices]
        form.fields["label"].set_filters(
            {"assessment_id": self.assessment.id, "published": True}
            if not self.perms["edit"]
            else {"assessment_id": self.assessment.id}
        )
        form.fields["label"].widget.attrs.update({"data-placeholder": "Tables with label applied"})
        form.fields["label"].widget.attrs["size"] = 1

        return form
