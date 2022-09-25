from django import forms
import django_filters as df
from django.db.models import QuerySet
from django.db.models.functions import Lower

from ..assessment.models import DoseUnits
from ..animal.models import Experiment, Endpoint
from ..animal.constants import ExperimentType
from ..study.models import Study


def is_boolean_true(queryset: QuerySet, name: str, value: bool) -> QuerySet:
    if value:
        return queryset.filter(**{name: True})
    return queryset


def distinct_term_choices(assessment_id: int, field: str) -> QuerySet:
    return (
        Endpoint.objects.filter(assessment_id=assessment_id)
        .order_by(field)
        .distinct(field)
        .values_list(field, field)
    )


class EndpointFilter(df.FilterSet):
    def __init__(self, *args, **kw):
        self.assessment_id = kw.pop("assessment_id")
        super().__init__(*args, **kw)

    def limit_filters(self):
        form = self.form
        form.fields["animal_group__experiment__type"].choices = [
            (el, ExperimentType(el).label)
            for el in Experiment.objects.filter(study__assessment_id=self.assessment_id)
            .values_list("type", flat=True)
            .distinct()
        ]

        form.fields["animal_group__experiment__study"].queryset = (
            Study.objects.assessment_qs(self.assessment_id)
            .filter(bioassay=True)
            .order_by(Lower("short_citation"))
        )
        form.fields[
            "animal_group__dosed_animals__doses__dose_units"
        ].queryset = DoseUnits.objects.get_animal_units(self.assessment_id)
        form.fields["system"].choices = distinct_term_choices(self.assessment_id, "system")
        form.fields["organ"].choices = distinct_term_choices(self.assessment_id, "organ")
        form.fields["effect"].choices = distinct_term_choices(self.assessment_id, "effect")
        form.fields["effect_subtype"].choices = distinct_term_choices(
            self.assessment_id, "effect_subtype"
        )

    animal_group__experiment__type = df.MultipleChoiceFilter(
        label="Experiment type", lookup_expr="exact", choices=ExperimentType.choices
    )
    animal_group__dosed_animals__doses__dose_units = df.ModelMultipleChoiceFilter(
        label="Dose Units", lookup_expr="exact", queryset=Study.objects.none()
    )
    animal_group__experiment__study = df.ModelMultipleChoiceFilter(
        label="Included studies", lookup_expr="exact", queryset=Study.objects.none()
    )
    system = df.MultipleChoiceFilter(lookup_expr="exact", choices=[])
    organ = df.MultipleChoiceFilter(lookup_expr="exact", choices=[])
    effect = df.MultipleChoiceFilter(lookup_expr="exact", choices=[])
    effect_subtype = df.MultipleChoiceFilter(lookup_expr="exact", choices=[])
    effects = df.MultipleChoiceFilter(lookup_expr="exact", choices=[])
    published_only = df.BooleanFilter(
        field_name="animal_group__experiment__study__published",
        label="Published only",
        widget=forms.CheckboxInput,
        method=is_boolean_true,
    )

    class Meta:
        model = Endpoint
        fields = [
            "animal_group__experiment__type",
            "animal_group__dosed_animals__doses__dose_units",
            "animal_group__experiment__study",
            "system",
            "organ",
            "effect",
            "effect_subtype",
            "effects",
            "published_only",
        ]
