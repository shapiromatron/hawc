import django_filters as df
from django.forms.widgets import CheckboxInput

from ..animal.models import Endpoint
from ..common.filterset import BaseFilterSet, filter_noop
from ..study.models import Study


class BioassayPrefilter(BaseFilterSet):
    # studies
    published_only = df.BooleanFilter(
        field_name="animal_group__experiment__study__published",
        widget=CheckboxInput(),
        label="Published studies only",
        help_text="Only present data from studies which have been marked as "
        '"published" in HAWC.',
    )
    prefilter_study = df.BooleanFilter(
        method=filter_noop,
        widget=CheckboxInput(),
        label="Prefilter by study",
        help_text="Prefilter endpoints to include only selected studies.",
    )
    studies = df.ModelMultipleChoiceFilter(
        field_name="animal_group__experiment__study",
        queryset=Study.objects.all(),
        label="Studies to include",
        help_text="""Select one or more studies to include in the plot.
                If no study is selected, no endpoints will be available.""",
    )
    # bioassay
    prefilter_system = df.BooleanFilter(
        method=filter_noop,
        widget=CheckboxInput(),
        label="Prefilter by system",
        help_text="Prefilter endpoints on plot to include selected systems.",
    )
    systems = df.MultipleChoiceFilter(
        field_name="system",
        label="Systems to include",
        help_text="""Select one or more systems to include in the plot.
                                 If no system is selected, no endpoints will be available.""",
    )
    prefilter_organ = df.BooleanFilter(
        method=filter_noop,
        widget=CheckboxInput(),
        label="Prefilter by organ",
        help_text="Prefilter endpoints on plot to include selected organs.",
    )
    organs = df.MultipleChoiceFilter(
        field_name="organ",
        label="Organs to include",
        help_text="""Select one or more organs to include in the plot.
                                 If no organ is selected, no endpoints will be available.""",
    )
    prefilter_effect = df.BooleanFilter(
        method=filter_noop,
        widget=CheckboxInput(),
        label="Prefilter by effect",
        help_text="Prefilter endpoints on plot to include selected effects.",
    )
    effects = df.MultipleChoiceFilter(
        field_name="effect",
        label="Effects to include",
        help_text="""Select one or more effects to include in the plot.
                                 If no effect is selected, no endpoints will be available.""",
    )
    prefilter_effect_subtype = df.BooleanFilter(
        method=filter_noop,
        widget=CheckboxInput(),
        label="Prefilter by effect sub-type",
        help_text="Prefilter endpoints on plot to include selected effects.",
    )
    effect_subtypes = df.MultipleChoiceFilter(
        field_name="effect_subtype",
        label="Effect Sub-Types to include",
        help_text="""Select one or more effect sub-types to include in the plot.
                                 If no effect sub-type is selected, no endpoints will be available.""",
    )

    class Meta:
        model = Endpoint
        fields = [
            "published_only",
            "prefilter_study",
            "studies",
            "prefilter_system",
            "systems",
            "prefilter_organ",
            "organs",
            "prefilter_effect",
            "effects",
            "prefilter_effect_subtype",
            "effect_subtypes",
        ]

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].queryset = Study.objects.filter(assessment=self.assessment)
        form.fields["systems"].choices = Endpoint.objects.get_system_choices(self.assessment.pk)
        form.fields["organs"].choices = Endpoint.objects.get_organ_choices(self.assessment.pk)
        form.fields["effects"].choices = Endpoint.objects.get_effect_choices(self.assessment.pk)
        form.fields["effect_subtypes"].choices = Endpoint.objects.get_effect_subtype_choices(
            self.assessment.pk
        )
        return form


class InvitroPrefilter(BaseFilterSet):
    pass
