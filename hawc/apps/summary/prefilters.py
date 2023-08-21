import django_filters as df
from django.forms.widgets import CheckboxInput
from django import forms
from enum import Enum

from ..assessment.constants import EpiVersion
from ..assessment.models import Assessment, EffectTag
from ..animal.models import Endpoint
from ..common.filterset import BaseFilterSet, filter_noop
from ..common.forms import BaseFormHelper
from ..study.models import Study
from ..epi.models import Outcome
from ..epiv2.models import DataExtraction
from ..epimeta.models import MetaResult
from ..invitro.models import IVEndpoint, IVEndpointCategory, IVChemical
from ..eco.models import Result

from .constants import StudyType, VisualType

class TestForm(forms.Form):
    
    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False

        return helper

def filter_published_only(queryset, name, value):
    if not value:
        return queryset
    return queryset.filter(**{name:True})


class BioassayPrefilter(BaseFilterSet):
    # studies
    animal_group__experiment__study__published = df.BooleanFilter(
        method=filter_published_only,
        widget=CheckboxInput(),
        label="Published studies only",
        help_text="Only present data from studies which have been marked as "
        '"published" in HAWC.',
    )
    animal_group__experiment__study__in = df.MultipleChoiceFilter(
        field_name="animal_group__experiment__study",
        label="Studies to include",
        help_text="""Select one or more studies to include in the plot.
                If no study is selected, no endpoints will be available.""",
    )
    # bioassay
    system__in = df.MultipleChoiceFilter(
        field_name="system",
        label="Systems to include",
        help_text="""Select one or more systems to include in the plot.
                                 If no system is selected, no endpoints will be available.""",
    )
    organ__in = df.MultipleChoiceFilter(
        field_name="organ",
        label="Organs to include",
        help_text="""Select one or more organs to include in the plot.
                                 If no organ is selected, no endpoints will be available.""",
    )
    effect__in = df.MultipleChoiceFilter(
        field_name="effect",
        label="Effects to include",
        help_text="""Select one or more effects to include in the plot.
                                 If no effect is selected, no endpoints will be available.""",
    )
    effect_subtype__in = df.MultipleChoiceFilter(
        field_name="effect_subtype",
        label="Effect Sub-Types to include",
        help_text="""Select one or more effect sub-types to include in the plot.
                                 If no effect sub-type is selected, no endpoints will be available.""",
    )
    effects__in = df.MultipleChoiceFilter(
        field_name="effects",
                            label="Tags to include",
                            help_text="""Select one or more effect-tags to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
    )

    class Meta:
        model = Endpoint
        fields = [
            "animal_group__experiment__study__published",
            "animal_group__experiment__study__in",
            "system__in",
            "organ__in",
            "effect__in",
            "effect_subtype__in","effects__in",
        ]
        form = TestForm

    def create_form(self):
        form = super().create_form()
        form.fields["animal_group__experiment__study__in"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["system__in"].choices = Endpoint.objects.get_system_choices(self.assessment.pk)
        form.fields["organ__in"].choices = Endpoint.objects.get_organ_choices(self.assessment.pk)
        form.fields["effect__in"].choices = Endpoint.objects.get_effect_choices(self.assessment.pk)
        form.fields["effect_subtype__in"].choices = Endpoint.objects.get_effect_subtype_choices(
            self.assessment.pk
        )
        form.fields["effects__in"].choices = EffectTag.objects.get_choices(self.assessment.pk)
        return form



class EpiV1Prefilter(BaseFilterSet):
    # studies
    study_population__study__published = df.BooleanFilter(
        method=filter_published_only,
        widget=CheckboxInput(),
        label="Published studies only",
        help_text="Only present data from studies which have been marked as "
        '"published" in HAWC.',
    )
    study_population__study__in = df.MultipleChoiceFilter(
        field_name="study_population__study",
        label="Studies to include",
        help_text="""Select one or more studies to include in the plot.
                If no study is selected, no endpoints will be available.""",
    )
    # epi
    system__in = df.MultipleChoiceFilter(
        field_name="system",
                            label="Systems to include",
                            help_text="""Select one or more systems to include in the plot.
                                 If no system is selected, no endpoints will be available.""",
    )
    effect__in = df.MultipleChoiceFilter(
        field_name="effect",
                            label="Effects to include",
                            help_text="""Select one or more effects to include in the plot.
                                 If no effect is selected, no endpoints will be available.""",
    )
    effects__in = df.MultipleChoiceFilter(
        field_name="effects",
                            label="Tags to include",
                            help_text="""Select one or more effect-tags to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
    )

    class Meta:
        model = Outcome
        fields = [
            "study_population__study__published",
            "study_population__study__in","system__in","effect__in","effects__in",
        ]
        form = TestForm

    def create_form(self):
        form = super().create_form()
        form.fields["study_population__study__in"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["system__in"].choices = Outcome.objects.get_system_choices(self.assessment.pk)
        form.fields["effect__in"].choices = Outcome.objects.get_effect_choices(self.assessment.pk)
        form.fields["effects__in"].choices = EffectTag.objects.get_choices(self.assessment.pk)
        return form

class EpiV2Prefilter(BaseFilterSet):
    # studies
    design__study__published = df.BooleanFilter(
        method=filter_published_only,
        widget=CheckboxInput(),
        label="Published studies only",
        help_text="Only present data from studies which have been marked as "
        '"published" in HAWC.',
    )
    design__study__in = df.MultipleChoiceFilter(
        field_name="design__study",
        label="Studies to include",
        help_text="""Select one or more studies to include in the plot.
                If no study is selected, no endpoints will be available.""",
    )

    class Meta:
        model = DataExtraction
        fields = [
            "design__study__published",
            "design__study__in",
        ]
        form = TestForm

    def create_form(self):
        form = super().create_form()
        form.fields["design__study__in"].choices = Study.objects.get_choices(self.assessment.pk)
        return form

class EpiMetaPrefilter(BaseFilterSet):
    # studies
    protocol__study__published = df.BooleanFilter(
        method=filter_published_only,
        widget=CheckboxInput(),
        label="Published studies only",
        help_text="Only present data from studies which have been marked as "
        '"published" in HAWC.',
    )
    protocol__study__in = df.MultipleChoiceFilter(
        field_name="protocol__study",
        label="Studies to include",
        help_text="""Select one or more studies to include in the plot.
                If no study is selected, no endpoints will be available.""",
    )

    class Meta:
        model = MetaResult
        fields = [
            "protocol__study__published",
            "protocol__study__in",
        ]
        form = TestForm

    def create_form(self):
        form = super().create_form()
        form.fields["protocol__study__in"].choices = Study.objects.get_choices(self.assessment.pk)
        return form

class InvitroPrefilter(BaseFilterSet):
    # studies
    experiment__study__published = df.BooleanFilter(
        method=filter_published_only,
        widget=CheckboxInput(),
        label="Published studies only",
        help_text="Only present data from studies which have been marked as "
        '"published" in HAWC.',
    )
    experiment__study__in = df.MultipleChoiceFilter(
        field_name="experiment__study",
        label="Studies to include",
        help_text="""Select one or more studies to include in the plot.
                If no study is selected, no endpoints will be available.""",
    )
    # invitro
    category__in = df.MultipleChoiceFilter(
        field_name="category",
                            label="Categories to include",
                            help_text="""Select one or more categories to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
    )
    chemical__name__in = df.MultipleChoiceFilter(
        field_name="chemical__name",
                            label="Chemicals to include",
                            help_text="""Select one or more chemicals to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
    )
    effects__in = df.MultipleChoiceFilter(
        field_name="effects",
                            label="Tags to include",
                            help_text="""Select one or more effect-tags to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
    )

    class Meta:
        model = IVEndpoint
        fields = [
            "experiment__study__published",
            "experiment__study__in","category__in","chemical__name__in","effects__in",
        ]
        form = TestForm

    def create_form(self):
        form = super().create_form()
        form.fields["experiment__study__in"].choices = Study.objects.get_choices(self.assessment.pk)
        form.fields["category__in"].choices = IVEndpointCategory.get_choices(self.assessment.pk)
        form.fields["chemical__name__in"].choices = IVChemical.objects.get_choices(self.assessment.pk)
        form.fields["effects__in"].choices = EffectTag.objects.get_choices(self.assessment.pk)
        return form


class StudyTypePrefilter(Enum):
    BIOASSAY = BioassayPrefilter
    EPIV1 = EpiV1Prefilter
    EPIV2 = EpiV2Prefilter
    EPI_META = EpiMetaPrefilter
    IN_VITRO = InvitroPrefilter

    @classmethod
    def from_study_type(cls,study_type:StudyType,assessment:Assessment):
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
    def from_visual_type(cls,visual_type:VisualType):
        visual_type = VisualType(visual_type)
        name = visual_type.name
        return cls[name]