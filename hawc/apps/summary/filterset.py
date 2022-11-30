import django_filters as df
from django.db.models import Q

from ..common.filterset import BaseFilterSet
from . import constants, models


class VisualFilterSet(BaseFilterSet):
    text = df.CharFilter(method="filter_text", label="Text", help_text="Title or description text")
    type = df.ChoiceFilter(
        field_name="visual_type",
        label="Visualization type",
        help_text="Type of visualization to display",
        empty_label="<All>",
    )
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC visualization",
        empty_label="<All>",
    )

    class Meta:
        model = models.Visual
        fields = ["text", "type", "published"]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        query = Q(assessment=self.assessment)
        if not self.perms["edit"]:
            query &= Q(published=True)
        return queryset.filter(query)

    def filter_text(self, queryset, name, value):
        query = Q(title__icontains=value) | Q(caption__icontains=value)
        return queryset.filter(query)

    def create_form(self):
        form = super().create_form()
        if not self.perms["edit"]:
            form.fields["published"].disabled = True
        choices = models.Visual.objects.filter(assessment=self.assessment).values_list(
            "visual_type", flat=True
        )
        choices = [constants.VisualType(choice) for choice in sorted(set(choices))]
        form.fields["type"].choices = [(choice.value, choice.label) for choice in choices]
        return form


class DataPivotFilterSet(VisualFilterSet):
    type = df.ChoiceFilter(
        field_name="datapivotquery__evidence_type",
        label="Visualization type",
        help_text="Type of visualization to display",
        empty_label="<All>",
    )

    class Meta(VisualFilterSet.Meta):
        model = models.DataPivot

    def create_form(self):
        form = super(VisualFilterSet, self).create_form()
        if not self.perms["edit"]:
            form.fields["published"].disabled = True
        choices = models.DataPivot.objects.filter(assessment=self.assessment).values_list(
            "datapivotquery__evidence_type", flat=True
        )
        choices = [constants.StudyType(choice) for choice in sorted(set(choices))]
        form.fields["type"].choices = [
            (choice.value, f"Data pivot ({choice.label})") for choice in choices
        ]
        return form


class SummaryTableFilterSet(BaseFilterSet):
    title = df.CharFilter(field_name="title", lookup_expr="icontains", label="Title")
    type = df.ChoiceFilter(
        field_name="table_type",
        label="Table type",
        help_text="Type of summary table to display",
        empty_label="<All>",
    )
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC summary tables",
        empty_label="<All>",
    )

    class Meta:
        model = models.SummaryTable
        fields = ["title", "type", "published"]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        query = Q(assessment=self.assessment)
        if not self.perms["edit"]:
            query &= Q(published=True)
        return queryset.filter(query)

    def create_form(self):
        form = super().create_form()
        if not self.perms["edit"]:
            form.fields["published"].disabled = True
        choices = models.SummaryTable.objects.filter(assessment=self.assessment).values_list(
            "table_type", flat=True
        )
        choices = [constants.TableType(choice) for choice in sorted(set(choices))]
        form.fields["type"].choices = [(choice.value, choice.label) for choice in choices]
        return form
