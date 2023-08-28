from enum import Enum

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


class TestForm(forms.Form):
    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False

        return helper


class BioassayPrefilter(BaseFilterSet):
    # studies
    published_only = df.BooleanFilter(
        method="filter_published_only",
        widget=CheckboxInput(),
        label="Published studies only",
        help_text='Only present data from studies which have been marked as "published" in HAWC.',
    )
    studies = df.MultipleChoiceFilter(
        field_name="animal_group__experiment__study",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )
    # bioassay
    systems = df.MultipleChoiceFilter(
        field_name="system",
        label="Systems to include",
        help_text="Select one or more systems to include in the plot.",
    )
    organs = df.MultipleChoiceFilter(
        field_name="organ",
        label="Organs to include",
        help_text="Select one or more organs to include in the plot.",
    )
    effects = df.MultipleChoiceFilter(
        field_name="effect",
        label="Effects to include",
        help_text="Select one or more effects to include in the plot.",
    )
    effect_subtypes = df.MultipleChoiceFilter(
        field_name="effect_subtype",
        label="Effect Sub-Types to include",
        help_text="Select one or more effect sub-types to include in the plot.",
    )
    effect_tags = df.MultipleChoiceFilter(
        field_name="effects",
        label="Tags to include",
        help_text="Select one or more effect-tags to include in the plot.",
    )

    class Meta:
        model = Endpoint
        fields = [
            "published_only",
            "studies",
            "systems",
            "organs",
            "effects",
            "effect_subtypes",
            "effect_tags",
        ]
        form = TestForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(animal_group__experiment__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["systems"].choices = Endpoint.objects.get_system_choices(self.assessment.pk)
        form.fields["organs"].choices = Endpoint.objects.get_organ_choices(self.assessment.pk)
        form.fields["effects"].choices = Endpoint.objects.get_effect_choices(self.assessment.pk)
        form.fields["effect_subtypes"].choices = Endpoint.objects.get_effect_subtype_choices(
            self.assessment.pk
        )
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)
        return form


class EpiV1Prefilter(BaseFilterSet):
    # studies
    published_only = df.BooleanFilter(
        method="filter_published_only",
        widget=CheckboxInput(),
        label="Published studies only",
        help_text='Only present data from studies which have been marked as "published" in HAWC.',
    )
    studies = df.MultipleChoiceFilter(
        field_name="study_population__study",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )
    # epi
    systems = df.MultipleChoiceFilter(
        field_name="system",
        label="Systems to include",
        help_text="Select one or more systems to include in the plot.",
    )
    effects = df.MultipleChoiceFilter(
        field_name="effect",
        label="Effects to include",
        help_text="Select one or more effects to include in the plot.",
    )
    effect_tags = df.MultipleChoiceFilter(
        field_name="effects",
        label="Tags to include",
        help_text="Select one or more effect-tags to include in the plot.",
    )

    class Meta:
        model = Outcome
        fields = [
            "published_only",
            "studies",
            "systems",
            "effects",
            "effect_tags",
        ]
        form = TestForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(study_population__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["systems"].choices = Outcome.objects.get_system_choices(self.assessment.pk)
        form.fields["effects"].choices = Outcome.objects.get_effect_choices(self.assessment.pk)
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)
        return form


class EpiV2Prefilter(BaseFilterSet):
    # studies
    published_only = df.BooleanFilter(
        method="filter_published_only",
        widget=CheckboxInput(),
        label="Published studies only",
        help_text='Only present data from studies which have been marked as "published" in HAWC.',
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
            "studies",
        ]
        form = TestForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(design__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(design__study__assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        return form


class EpiMetaPrefilter(BaseFilterSet):
    # studies
    published_only = df.BooleanFilter(
        method="filter_published_only",
        widget=CheckboxInput(),
        label="Published studies only",
        help_text='Only present data from studies which have been marked as "published" in HAWC.',
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
            "studies",
        ]
        form = TestForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(protocol__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(protocol__study__assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        return form


class InvitroPrefilter(BaseFilterSet):
    # studies
    published_only = df.BooleanFilter(
        method="filter_published_only",
        widget=CheckboxInput(),
        label="Published studies only",
        help_text='Only present data from studies which have been marked as "published" in HAWC.',
    )
    studies = df.MultipleChoiceFilter(
        field_name="experiment__study",
        label="Studies to include",
        help_text="Select one or more studies to include in the plot.",
    )
    # invitro
    categories = df.MultipleChoiceFilter(
        field_name="category",
        label="Categories to include",
        help_text="Select one or more categories to include in the plot.",
    )
    chemicals = df.MultipleChoiceFilter(
        field_name="chemical__name",
        label="Chemicals to include",
        help_text="Select one or more chemicals to include in the plot.",
    )
    effect_tags = df.MultipleChoiceFilter(
        field_name="effects",
        label="Tags to include",
        help_text="Select one or more effect-tags to include in the plot.",
    )

    class Meta:
        model = IVEndpoint
        fields = [
            "published_only",
            "studies",
            "categories",
            "chemicals",
            "effect_tags",
        ]
        form = TestForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(experiment__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["categories"].choices = IVEndpointCategory.get_choices(self.assessment.pk)
        form.fields["chemicals"].choices = IVChemical.objects.get_choices(self.assessment.pk)
        form.fields["effect_tags"].choices = EffectTag.objects.get_choices(self.assessment.pk)
        return form


class EcoPrefilter(BaseFilterSet):
    # studies
    published_only = df.BooleanFilter(
        method="filter_published_only",
        widget=CheckboxInput(),
        label="Published studies only",
        help_text='Only present data from studies which have been marked as "published" in HAWC.',
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
            "studies",
        ]
        form = TestForm

    def filter_published_only(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(design__study__published=True)

    def filter_queryset(self, queryset):
        queryset = queryset.filter(design__study__assessment_id=self.assessment.pk)
        return super().filter_queryset(queryset)

    def create_form(self):
        form = super().create_form()
        form.fields["studies"].choices = Study.objects.get_choices(self.assessment.pk)
        return form


class StudyTypePrefilter(Enum):
    BIOASSAY = BioassayPrefilter
    EPIV1 = EpiV1Prefilter
    EPIV2 = EpiV2Prefilter
    EPI_META = EpiMetaPrefilter
    IN_VITRO = InvitroPrefilter
    ECO = EcoPrefilter

    @classmethod
    def from_study_type(cls, study_type: int | StudyType, assessment: Assessment):
        study_type = StudyType(study_type)
        name = study_type.name
        if study_type == StudyType.EPI:
            if assessment.epi_version == EpiVersion.V1:
                name = "EPIV1"
            elif assessment.epi_version == EpiVersion.V2:
                name = "EPIV2"
        return cls[name]


class VisualTypePrefilter(Enum):
    BIOASSAY_CROSSVIEW = BioassayPrefilter
    ROB_HEATMAP = BioassayPrefilter
    ROB_BARCHART = BioassayPrefilter

    @classmethod
    def from_visual_type(cls, visual_type: int | VisualType):
        visual_type = VisualType(visual_type)
        name = visual_type.name
        return cls[name]
