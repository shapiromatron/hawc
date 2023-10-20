import django_filters as df
from django.forms.widgets import CheckboxInput

from ...eco.models import Result
from ...study.models import Study
from .base import PrefilterBaseFilterSet, PrefilterForm


class EcoResultPrefilter(PrefilterBaseFilterSet):
    # studies
    published_only = df.BooleanFilter(
        method="filter_published_only",
        widget=CheckboxInput(),
        label="Published studies only",
        help_text='Only present data from studies which have been marked as "published" in HAWC.',
    )
    cb_studies = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "studies"}),
        label="Prefilter by study",
        help_text="Prefilter endpoints to include only selected studies.",
    )
    studies = df.MultipleChoiceFilter(
        field_name="design__study",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )

    class Meta:
        model = Result
        fields = [
            "published_only",
            "cb_studies",
            "studies",
        ]
        form = PrefilterForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(design__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(design__study__assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def set_passthrough_options(self, form):
        self._set_passthrough_choices(form, ["studies"])

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
