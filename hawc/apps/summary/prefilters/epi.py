import django_filters as df
from django.forms.widgets import CheckboxInput

from ...assessment.models import EffectTag
from ...epi.models import Outcome
from ...study.models import Study
from .base import PrefilterBaseFilterSet, PrefilterForm


class EpiV1ResultPrefilter(PrefilterBaseFilterSet):
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
        field_name="study_population__study",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )
    # epi
    cb_systems = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "systems"}),
        label="Prefilter by system",
        help_text="Prefilter endpoints to include only selected systems.",
    )
    systems = df.MultipleChoiceFilter(
        field_name="system",
        label="Systems to include",
        help_text="Select one or more systems to include in the plot.",
    )
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
        model = Outcome
        fields = [
            "published_only",
            "cb_studies",
            "studies",
            "cb_systems",
            "systems",
            "cb_effects",
            "effects",
            "cb_effect_tags",
            "effect_tags",
        ]
        form = PrefilterForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(study_population__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def set_passthrough_options(self, form):
        self._set_passthrough_choices(form, ["studies", "systems", "effects", "effect_tags"])

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["systems"].choices = Outcome.objects.get_system_choices(self.assessment.pk)
        form.fields["effects"].choices = Outcome.objects.get_effect_choices(self.assessment.pk)
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)
