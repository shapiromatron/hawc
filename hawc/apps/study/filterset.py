import django_filters as df
from django.db.models import Q

from ..animal.models import Experiment
from ..common.filterset import BaseFilterSet
from ..epi.models import Exposure
from ..myuser.models import HAWCUser
from . import constants, models


class StudyFilterSet(BaseFilterSet):
    citation = df.CharFilter(
        method="filter_citation", label="Citation", help_text="Authors, year, title, etc."
    )
    identifier = df.CharFilter(
        field_name="identifiers__unique_id",
        lookup_expr="icontains",
        label="Identifier",
        help_text="Database identifier<br/>(PubMed ID, DOI, HERO ID, etc)",
    )
    data_type = df.ChoiceFilter(
        method="filter_data_type",
        choices=constants.StudyTypeChoices.filtered_choices(),
        label="Data type",
        help_text="Data type for full-text extraction",
        empty_label="<All>",
    )
    published = df.ChoiceFilter(
        choices=[(True, "Published only"), (False, "Unpublished only")],
        label="Published",
        help_text="Published status for HAWC extraction",
        empty_label="<All>",
    )
    assigned_user = df.ModelChoiceFilter(
        method="filter_assigned_user",
        queryset=HAWCUser.objects.all(),
        label="Assigned user",
        help_text="A user with active study evaluation assignments",
        empty_label="<All>",
    )

    class Meta:
        model = models.Study
        fields = ["citation", "identifier", "data_type", "published", "assigned_user"]
        grid_layout = {
            "rows": [
                {"columns": [{"width": 4}, {"width": 2}, {"width": 2}, {"width": 2}, {"width": 2}]},
            ]
        }

    def __init__(self, *args, assessment, include_rob_authors=False, **kwargs):
        self.include_rob_authors = include_rob_authors
        super().__init__(*args, assessment=assessment, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        query = Q(assessment=self.assessment)
        if not self.perms["edit"]:
            query &= Q(published=True)
        return queryset.filter(query)

    def filter_citation(self, queryset, name, value):
        query = Q(short_citation__icontains=value) | Q(full_citation__icontains=value)
        return queryset.filter(query)

    def filter_data_type(self, queryset, name, value):
        return queryset.filter(**{value: True})

    def filter_assigned_user(self, queryset, name, value):
        return queryset.filter(riskofbiases__author=value, riskofbiases__active=True).distinct()

    def create_form(self):
        form = super().create_form()
        form.fields["assigned_user"].queryset = self.assessment.pms_and_team_users()
        if not self.include_rob_authors:
            form.fields.pop("assigned_user")
        if not self.perms["edit"]:
            form.fields.pop("published")
        if len(form.fields) == 4:
            columns = form.grid_layout.rows[0].columns
            del columns[-1 : len(columns)]
            for column in columns:
                column.width = 3
        if len(form.fields) == 3:
            columns = form.grid_layout.rows[0].columns
            del columns[-2 : len(columns)]
            for column in columns:
                column.width = 4
        return form


class GlobalReferencesFilterSet(df.FilterSet):
    query = df.CharFilter(method="filter_animal_level_data", label="Query")
    published = df.BooleanFilter(method="filter_published")

    def filter_animal_level_data(self, queryset, name, value):
        query = (
            Q(chemical__icontains=value)
            | Q(cas=value)
            | Q(dtxsid__dtxsid=value)
            | Q(dtxsid__content__preferredName__icontains=value)
            | Q(dtxsid__content__casrn=value)
        )
        return queryset.filter(query).values_list("id", "study__assessment__name").distinct()

    def filter_published(self, queryset, name, value):
        if value is True:
            return queryset.filter(study__published=True)
        else:
            return queryset.filter(study__published=False)

    class Meta:
        model = Experiment
        fields = ["chemical", "dtxsid__dtxsid", "cas", "type", "study__published"]


class GlobalEpiFilterSet(df.FilterSet):
    query = df.CharFilter(method="filter_epi_level_data")
    published = df.BooleanFilter(method="filter_published")

    def filter_epi_level_data(self, queryset, name, value):
        query = (
            Q(name__icontains=value)
            | Q(dtxsid__dtxsid=value)
            | Q(dtxsid__content__preferredName__icontains=value)
        )
        # no cas data ?
        return (
            queryset.filter(query)
            .values_list("id", "study_population__study___assessment__name")
            .distinct()
        )

    class Meta:
        model = Exposure
        fields = ["name", "dtxsid__dtxsid", "study_population__study__published"]
