import django_filters as df
from django.forms.widgets import CheckboxInput

from ...assessment.models import EffectTag
from ...invitro.models import IVChemical, IVEndpoint, IVEndpointCategory
from ...study.models import Study
from .base import PrefilterBaseFilterSet, PrefilterForm


class InvitroOutcomePrefilter(PrefilterBaseFilterSet):
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
        field_name="experiment__study",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )
    # invitro
    cb_effects = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "effects"}),
        label="Prefilter by effect",
        help_text="Prefilter endpoints to include only selected effects.",
    )
    effects = df.MultipleChoiceFilter(
        field_name="effect",
        label="Effects to include",
        help_text="Select one or more effects to include in the plot.",
    )
    cb_categories = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "categories"}),
        label="Prefilter by category",
        help_text="Prefilter endpoints to include only selected categories.",
    )
    categories = df.MultipleChoiceFilter(
        field_name="category",
        label="Categories to include",
        help_text="Select one or more categories to include in the plot.",
    )
    cb_chemicals = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "chemicals"}),
        label="Prefilter by chemical",
        help_text="Prefilter endpoints to include only selected chemicals.",
    )
    chemicals = df.MultipleChoiceFilter(
        field_name="chemical__name",
        label="Chemicals to include",
        help_text="Select one or more chemicals to include in the plot.",
    )
    cb_effect_tags = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "effect_tags"}),
        label="Prefilter by effect tag",
        help_text="Prefilter endpoints to include only selected effect tags.",
    )
    effect_tags = df.MultipleChoiceFilter(
        field_name="effects",
        label="Tags to include",
        help_text="Select one or more effect tags to include in the plot.",
    )

    class Meta:
        model = IVEndpoint
        fields = [
            "published_only",
            "cb_studies",
            "studies",
            "cb_effects",
            "effects",
            "cb_categories",
            "categories",
            "cb_chemicals",
            "chemicals",
            "cb_effect_tags",
            "effect_tags",
        ]
        form = PrefilterForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(experiment__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def set_passthrough_options(self, form):
        self._set_passthrough_choices(
            form, ["studies", "effects", "categories", "chemicals", "effect_tags"]
        )

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["effects"].choices = IVEndpoint.objects.get_effect_choices(self.assessment.pk)
        form.fields["categories"].choices = IVEndpointCategory.get_choices(self.assessment.pk)
        form.fields["chemicals"].choices = IVChemical.objects.get_choices(self.assessment.pk)
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)
