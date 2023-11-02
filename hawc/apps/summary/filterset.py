import django_filters as df
from django.db.models import Q

from ..assessment.constants import RobName
from ..common.filterset import BaseFilterSet, InlineFilterForm
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
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC visualization",
        empty_label="Published status",
    )

    class Meta:
        model = models.Visual
        fields = ["title", "type", "published"]
        form = InlineFilterForm

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        query = Q(assessment=self.assessment)
        if not self.perms["edit"]:
            query &= Q(published=True)
        return queryset.filter(query).order_by("id")

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
        return form


class DataPivotFilterSet(VisualFilterSet):
    type = df.ChoiceFilter(
        method="filter_evidence_type",
        label="Visualization type",
        help_text="Type of visualization to display",
        empty_label="<All>",
    )

    class Meta(VisualFilterSet.Meta):
        model = models.DataPivot

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).select_related("datapivotquery", "datapivotupload")

    def get_type_choices(self):
        choice_options = (
            models.DataPivot.objects.filter(assessment=self.assessment)
            .values_list("datapivotquery__evidence_type", flat=True)
            .distinct()
        )
        choice_options = map(lambda x: x if x is not None else 999, choice_options)
        choices = []
        for choice in sorted(set(choice_options)):
            try:
                choice = constants.StudyType(choice)
                choices.append((choice.value, f"Data pivot ({choice.label})"))
            except ValueError:
                choices.append((999, "Data pivot (File Upload)"))
        return choices

    def filter_evidence_type(self, queryset, name, value):
        value = int(value)
        if value == 999:
            return queryset.filter(datapivotupload__id__gt=0)
        return queryset.filter(datapivotquery__evidence_type=value)


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
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC summary tables",
        empty_label="Published status",
    )

    class Meta:
        model = models.SummaryTable
        fields = ["title", "type", "published"]
        form = InlineFilterForm

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        query = Q(assessment=self.assessment)
        if not self.perms["edit"]:
            query &= Q(published=True)
        return queryset.filter(query).order_by("id")

    def create_form(self):
        form = super().create_form()

        # set type choices based on what is available
        choices = models.SummaryTable.objects.filter(assessment=self.assessment).values_list(
            "table_type", flat=True
        )
        choices = [constants.TableType(choice) for choice in sorted(set(choices))]
        form.fields["type"].choices = [(choice.value, choice.label) for choice in choices]

        return form
