import django_filters as df
from django.forms.widgets import CheckboxInput

from ...animal.models import Endpoint
from ...assessment.models import EffectTag
from ...study.models import Study
from .base import PrefilterBaseFilterSet, PrefilterForm


class BioassayStudyPrefilter(PrefilterBaseFilterSet):
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
        field_name="pk",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )
    # bioassay
    cb_systems = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "systems"}),
        label="Prefilter by system",
        help_text="Prefilter endpoints to include only selected systems.",
    )
    systems = df.MultipleChoiceFilter(
        field_name="experiments__animal_groups__system",
        label="Systems to include",
        help_text="Select one or more systems to include in the plot.",
    )
    cb_organs = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "organs"}),
        label="Prefilter by organ",
        help_text="Prefilter endpoints to include only selected organs.",
    )
    organs = df.MultipleChoiceFilter(
        field_name="experiments__animal_groups__organ",
        label="Organs to include",
        help_text="Select one or more organs to include in the plot.",
    )
    cb_effects = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "effects"}),
        label="Prefilter by effect",
        help_text="Prefilter endpoints to include only selected effects.",
    )
    effects = df.MultipleChoiceFilter(
        field_name="experiments__animal_groups__effect",
        label="Effects to include",
        help_text="Select one or more effects to include in the plot.",
    )
    cb_effect_subtypes = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "effect_subtypes"}),
        label="Prefilter by effect subtype",
        help_text="Prefilter endpoints to include only selected effect subtypes.",
    )
    effect_subtypes = df.MultipleChoiceFilter(
        field_name="experiments__animal_groups__effect_subtype",
        label="Effect Sub-Types to include",
        help_text="Select one or more effect sub-types to include in the plot.",
    )
    cb_effect_tags = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "effect_tags"}),
        label="Prefilter by effect tag",
        help_text="Prefilter endpoints to include only selected effect tags.",
    )
    effect_tags = df.MultipleChoiceFilter(
        field_name="experiments__animal_groups__effects",
        label="Tags to include",
        help_text="Select one or more effect tags to include in the plot.",
    )

    class Meta:
        model = Study
        fields = [
            "published_only",
            "cb_studies",
            "studies",
            "cb_systems",
            "systems",
            "cb_organs",
            "organs",
            "cb_effects",
            "effects",
            "cb_effect_subtypes",
            "effect_subtypes",
            "cb_effect_tags",
            "effect_tags",
        ]
        form = PrefilterForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def set_passthrough_options(self, form):
        self._set_passthrough_choices(
            form, ["studies", "systems", "organs", "effects", "effect_subtypes", "effect_tags"]
        )

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["systems"].choices = Endpoint.objects.get_system_choices(self.assessment.pk)
        form.fields["organs"].choices = Endpoint.objects.get_organ_choices(self.assessment.pk)
        form.fields["effects"].choices = Endpoint.objects.get_effect_choices(self.assessment.pk)
        form.fields["effect_subtypes"].choices = Endpoint.objects.get_effect_subtype_choices(
            self.assessment.pk
        )
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)


class BioassayEndpointPrefilter(PrefilterBaseFilterSet):
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
        field_name="animal_group__experiment__study",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )
    # bioassay
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
    cb_organs = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "organs"}),
        label="Prefilter by organ",
        help_text="Prefilter endpoints to include only selected organs.",
    )
    organs = df.MultipleChoiceFilter(
        field_name="organ",
        label="Organs to include",
        help_text="Select one or more organs to include in the plot.",
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
    cb_effect_subtypes = df.BooleanFilter(
        method="noop",
        widget=CheckboxInput(attrs={"data-pf": "effect_subtypes"}),
        label="Prefilter by effect subtype",
        help_text="Prefilter endpoints to include only selected effect subtypes.",
    )
    effect_subtypes = df.MultipleChoiceFilter(
        field_name="effect_subtype",
        label="Effect Sub-Types to include",
        help_text="Select one or more effect sub-types to include in the plot.",
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
        model = Endpoint
        fields = [
            "published_only",
            "cb_studies",
            "studies",
            "cb_systems",
            "systems",
            "cb_organs",
            "organs",
            "cb_effects",
            "effects",
            "cb_effect_subtypes",
            "effect_subtypes",
            "cb_effect_tags",
            "effect_tags",
        ]
        form = PrefilterForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(animal_group__experiment__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def set_passthrough_options(self, form):
        self._set_passthrough_choices(
            form, ["studies", "systems", "organs", "effects", "effect_subtypes", "effect_tags"]
        )

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["systems"].choices = Endpoint.objects.get_system_choices(self.assessment.pk)
        form.fields["organs"].choices = Endpoint.objects.get_organ_choices(self.assessment.pk)
        form.fields["effects"].choices = Endpoint.objects.get_effect_choices(self.assessment.pk)
        form.fields["effect_subtypes"].choices = Endpoint.objects.get_effect_subtype_choices(
            self.assessment.pk
        )
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)
