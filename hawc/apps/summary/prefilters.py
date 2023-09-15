from enum import Enum
from typing import Self

import django_filters as df
from django import forms
from django.forms.widgets import CheckboxInput

from ..animal.models import Endpoint
from ..assessment.constants import EpiVersion
from ..assessment.models import Assessment, EffectTag
from ..common.filterset import BaseFilterSet
from ..common.forms import BaseFormHelper
from ..eco.models import Result
from ..epi.models import Outcome
from ..epimeta.models import MetaResult
from ..epiv2.models import DataExtraction
from ..invitro.models import IVChemical, IVEndpoint, IVEndpointCategory
from ..study.models import Study
from .constants import StudyType, VisualType


class PrefilterForm(forms.Form):
    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        return helper


class PrefilterBase(BaseFilterSet):
    def noop(self, queryset, name, value):
        return queryset


class BioassayEndpointPrefilter(PrefilterBase):
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
        set_passthrough_choices(
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


class EpiV1ResultPrefilter(PrefilterBase):
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
        set_passthrough_choices(form, ["studies", "systems", "effects", "effect_tags"])

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["systems"].choices = Outcome.objects.get_system_choices(self.assessment.pk)
        form.fields["effects"].choices = Outcome.objects.get_effect_choices(self.assessment.pk)
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)


class EpiV2ResultPrefilter(PrefilterBase):
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
        model = DataExtraction
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
        set_passthrough_choices(form, ["studies"])

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)


class EpiMetaResultPrefilter(PrefilterBase):
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
        field_name="protocol__study",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )

    class Meta:
        model = MetaResult
        fields = [
            "published_only",
            "cb_studies",
            "studies",
        ]
        form = PrefilterForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(protocol__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(protocol__study__assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def set_passthrough_options(self, form):
        set_passthrough_choices(form, ["studies"])

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)


class InvitroOutcomePrefilter(PrefilterBase):
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
        set_passthrough_choices(
            form, ["studies", "effects", "categories", "chemicals", "effect_tags"]
        )

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["effects"].choices = IVEndpoint.objects.get_effect_choices(self.assessment.pk)
        form.fields["categories"].choices = IVEndpointCategory.get_choices(self.assessment.pk)
        form.fields["chemicals"].choices = IVChemical.objects.get_choices(self.assessment.pk)
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)


def set_passthrough_choices(form: forms.Form, field_names: list[str]):
    for field_name in field_names:
        form.fields[field_name].choices = [(v, v) for v in form.data.get(field_name, [])]


class EcoResultPrefilter(BaseFilterSet):
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
        set_passthrough_choices(form, ["studies"])

    def set_form_options(self, form):
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)


class StudyTypePrefilter(Enum):
    BIOASSAY = BioassayEndpointPrefilter
    EPIV1 = EpiV1ResultPrefilter
    EPIV2 = EpiV2ResultPrefilter
    EPI_META = EpiMetaResultPrefilter
    IN_VITRO = InvitroOutcomePrefilter
    ECO = EcoResultPrefilter

    @classmethod
    def from_study_type(cls, study_type: int | StudyType, assessment: Assessment) -> Self:
        study_type = StudyType(study_type)
        name = study_type.name
        if study_type == StudyType.EPI:
            if assessment.epi_version == EpiVersion.V1:
                name = "EPIV1"
            elif assessment.epi_version == EpiVersion.V2:
                name = "EPIV2"
        return cls[name]


class VisualTypePrefilter(Enum):
    BIOASSAY_CROSSVIEW = BioassayEndpointPrefilter
    ROB_HEATMAP = BioassayEndpointPrefilter
    ROB_BARCHART = BioassayEndpointPrefilter

    @classmethod
    def from_visual_type(cls, visual_type: int | VisualType) -> Self:
        visual_type = VisualType(visual_type)
        name = visual_type.name
        return cls[name]
