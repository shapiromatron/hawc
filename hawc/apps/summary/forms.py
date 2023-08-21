import json
from urllib.parse import urlparse, urlunparse

import pandas as pd
import plotly.io as pio
from django import forms
from django.urls import reverse
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from ..animal.autocomplete import EndpointAutocomplete
from ..animal.models import Endpoint
from ..assessment.models import DoseUnits, EffectTag
from ..common import validators
from ..common.autocomplete import AutocompleteChoiceField
from ..common.forms import BaseFormHelper, QuillField, check_unique_for_assessment, DynamicFormField
from ..common.helper import new_window_a
from ..common.validators import validate_html_tags, validate_hyperlinks, validate_json_pydantic
from ..epi.models import Outcome
from ..invitro.models import IVChemical, IVEndpointCategory
from ..lit.models import ReferenceFilterTag
from ..study.autocomplete import StudyAutocomplete
from ..study.models import Study
from . import autocomplete, constants, models, prefilters


class PrefilterMixin:
    PREFILTER_COMBO_FIELDS = [
        "studies",
        "systems",
        "organs",
        "effects",
        "effect_subtypes",
        "episystems",
        "epieffects",
        "iv_categories",
        "iv_chemicals",
        "effect_tags",
    ]

    def createFields(self):
        fields = dict()
        epi_version = self.instance.assessment.epi_version

        if "study" in self.prefilter_include:
            fields.update(
                [
                    (
                        "published_only",
                        forms.BooleanField(
                            required=False,
                            initial=True,
                            label="Published studies only",
                            help_text="Only present data from studies which have been marked as "
                            '"published" in HAWC.',
                        ),
                    ),
                    (
                        "prefilter_study",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by study",
                            help_text="Prefilter endpoints to include only selected studies.",
                        ),
                    ),
                    (
                        "studies",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Studies to include",
                            help_text="""Select one or more studies to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
                        ),
                    ),
                ]
            )

        if "bioassay" in self.prefilter_include:
            fields.update(
                [
                    (
                        "prefilter_system",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by system",
                            help_text="Prefilter endpoints on plot to include selected systems.",
                        ),
                    ),
                    (
                        "systems",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Systems to include",
                            help_text="""Select one or more systems to include in the plot.
                                 If no system is selected, no endpoints will be available.""",
                        ),
                    ),
                    (
                        "prefilter_organ",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by organ",
                            help_text="Prefilter endpoints on plot to include selected organs.",
                        ),
                    ),
                    (
                        "organs",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Organs to include",
                            help_text="""Select one or more organs to include in the plot.
                                 If no organ is selected, no endpoints will be available.""",
                        ),
                    ),
                    (
                        "prefilter_effect",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by effect",
                            help_text="Prefilter endpoints on plot to include selected effects.",
                        ),
                    ),
                    (
                        "effects",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Effects to include",
                            help_text="""Select one or more effects to include in the plot.
                                 If no effect is selected, no endpoints will be available.""",
                        ),
                    ),
                    (
                        "prefilter_effect_subtype",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by effect sub-type",
                            help_text="Prefilter endpoints on plot to include selected effects.",
                        ),
                    ),
                    (
                        "effect_subtypes",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Effect Sub-Types to include",
                            help_text="""Select one or more effect sub-types to include in the plot.
                                 If no effect sub-type is selected, no endpoints will be available.""",
                        ),
                    ),
                ]
            )

        if "epi" in self.prefilter_include and epi_version == 1:
            fields.update(
                [
                    (
                        "prefilter_episystem",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by system",
                            help_text="Prefilter endpoints on plot to include selected systems.",
                        ),
                    ),
                    (
                        "episystems",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Systems to include",
                            help_text="""Select one or more systems to include in the plot.
                                 If no system is selected, no endpoints will be available.""",
                        ),
                    ),
                    (
                        "prefilter_epieffect",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by effect",
                            help_text="Prefilter endpoints on plot to include selected effects.",
                        ),
                    ),
                    (
                        "epieffects",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Effects to include",
                            help_text="""Select one or more effects to include in the plot.
                                 If no effect is selected, no endpoints will be available.""",
                        ),
                    ),
                ]
            )

        if "invitro" in self.prefilter_include:
            fields.update(
                [
                    (
                        "prefilter_iv_category",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by category",
                            help_text="Prefilter endpoints to include only selected category.",
                        ),
                    ),
                    (
                        "iv_categories",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Categories to include",
                            help_text="""Select one or more categories to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
                        ),
                    ),
                    (
                        "prefilter_iv_chemical",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by chemical",
                            help_text="Prefilter endpoints to include only selected chemicals.",
                        ),
                    ),
                    (
                        "iv_chemicals",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Chemicals to include",
                            help_text="""Select one or more chemicals to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
                        ),
                    ),
                ]
            )

        if "effect_tags" in self.prefilter_include:
            fields.update(
                [
                    (
                        "prefilter_effect_tag",
                        forms.BooleanField(
                            required=False,
                            label="Prefilter by effect-tag",
                            help_text="Prefilter endpoints to include only selected effect-tags.",
                        ),
                    ),
                    (
                        "effect_tags",
                        forms.MultipleChoiceField(
                            required=False,
                            widget=forms.SelectMultiple,
                            label="Tags to include",
                            help_text="""Select one or more effect-tags to include in the plot.
                                 If no study is selected, no endpoints will be available.""",
                        ),
                    ),
                ]
            )

        for k, v in fields.items():
            self.fields[k] = v

    def setInitialValues(self):
        is_new = self.initial == {}
        try:
            prefilters = json.loads(self.initial.get("prefilters", "{}"))
        except ValueError:
            prefilters = {}

        if type(self.instance) is models.Visual:
            evidence_type = constants.StudyType.BIOASSAY
        else:
            evidence_type = self.initial.get("evidence_type") or self.instance.evidence_type
        for k, v in prefilters.items():
            if k == "system__in":
                if evidence_type == constants.StudyType.BIOASSAY:
                    self.fields["prefilter_system"].initial = True
                    self.fields["systems"].initial = v
                elif evidence_type == constants.StudyType.EPI:
                    self.fields["prefilter_episystem"].initial = True
                    self.fields["episystems"].initial = v

            if k == "organ__in":
                self.fields["prefilter_organ"].initial = True
                self.fields["organs"].initial = v

            if k == "effect__in":
                if evidence_type == constants.StudyType.BIOASSAY:
                    self.fields["prefilter_effect"].initial = True
                    self.fields["effects"].initial = v
                elif evidence_type == constants.StudyType.EPI:
                    self.fields["prefilter_epieffect"].initial = True
                    self.fields["epieffects"].initial = v

            if k == "effect_subtype__in":
                self.fields["prefilter_effect_subtype"].initial = True
                self.fields["effect_subtypes"].initial = v

            if k == "effects__in":
                self.fields["prefilter_effect_tag"].initial = True
                self.fields["effect_tags"].initial = v

            if k == "category__in":
                self.fields["prefilter_iv_category"].initial = True
                self.fields["iv_categories"].initial = v

            if k == "chemical__name__in":
                self.fields["prefilter_iv_chemical"].initial = True
                self.fields["iv_chemicals"].initial = v

            if k in [
                "animal_group__experiment__study__in",
                "study_population__study__in",
                "experiment__study__in",
                "protocol__study__in",
                "design__study__in",
            ]:
                self.fields["prefilter_study"].initial = True
                self.fields["studies"].initial = v

        if self.__class__.__name__ == "CrossviewForm":
            published_only = prefilters.get("animal_group__experiment__study__published", False)
            if is_new:
                published_only = True
            self.fields["published_only"].initial = published_only

        for fldname in self.PREFILTER_COMBO_FIELDS:
            field = self.fields.get(fldname)
            if field:
                field.choices = self.getPrefilterQueryset(fldname)

    def getPrefilterQueryset(self, field_name):
        assessment_id = self.instance.assessment_id
        choices = None

        if field_name == "systems":
            choices = Endpoint.objects.get_system_choices(assessment_id)
        elif field_name == "organs":
            choices = Endpoint.objects.get_organ_choices(assessment_id)
        elif field_name == "effects":
            choices = Endpoint.objects.get_effect_choices(assessment_id)
        elif field_name == "effect_subtypes":
            choices = Endpoint.objects.get_effect_subtype_choices(assessment_id)
        elif field_name == "iv_categories":
            choices = IVEndpointCategory.get_choices(assessment_id)
        elif field_name == "iv_chemicals":
            choices = IVChemical.objects.get_choices(assessment_id)
        elif field_name == "effect_tags":
            choices = EffectTag.objects.get_choices(assessment_id)
        elif field_name == "studies":
            choices = Study.objects.get_choices(assessment_id)
        elif field_name == "episystems":
            choices = Outcome.objects.get_system_choices(assessment_id)
        elif field_name == "epieffects":
            choices = Outcome.objects.get_effect_choices(assessment_id)
        else:
            raise ValueError(f"Unknown field name: {field_name}")

        return choices

    def setFieldStyles(self):
        if self.fields.get("prefilters"):
            self.fields["prefilters"].widget = forms.HiddenInput()

        for fldname in self.PREFILTER_COMBO_FIELDS:
            field = self.fields.get(fldname)
            if field:
                field.widget.attrs["size"] = 10

    def setPrefilters(self, data):
        prefilters = {}
        epi_version = self.instance.assessment.epi_version

        if data.get("prefilter_study") is True:
            studies = data.get("studies", [])

            evidence_type = data.get("evidence_type", None)
            if self.__class__.__name__ == "CrossviewForm":
                evidence_type = 0

            if evidence_type == constants.StudyType.BIOASSAY:
                prefilters["animal_group__experiment__study__in"] = studies
            elif evidence_type == constants.StudyType.IN_VITRO:
                prefilters["experiment__study__in"] = studies
            elif evidence_type == constants.StudyType.EPI:
                if epi_version == 1:
                    prefilters["study_population__study__in"] = studies
                elif epi_version == 2:
                    prefilters["design__study__in"] = studies
                else:
                    raise ValueError("Invalid epi_version")
            elif evidence_type == constants.StudyType.EPI_META:
                prefilters["protocol__study__in"] = studies
            else:
                raise ValueError("Unknown evidence type")

        if data.get("prefilter_system") is True:
            prefilters["system__in"] = data.get("systems", [])

        if data.get("prefilter_organ") is True:
            prefilters["organ__in"] = data.get("organs", [])

        if data.get("prefilter_effect") is True:
            prefilters["effect__in"] = data.get("effects", [])

        if data.get("prefilter_effect_subtype") is True:
            prefilters["effect_subtype__in"] = data.get("effect_subtypes", [])

        if data.get("prefilter_episystem") is True:
            prefilters["system__in"] = data.get("episystems", [])

        if data.get("prefilter_epieffect") is True:
            prefilters["effect__in"] = data.get("epieffects", [])

        if data.get("prefilter_iv_category") is True:
            prefilters["category__in"] = data.get("iv_categories", [])

        if data.get("prefilter_iv_chemical") is True:
            prefilters["chemical__name__in"] = data.get("iv_chemicals", [])

        if data.get("prefilter_effect_tag") is True:
            prefilters["effects__in"] = data.get("effect_tags", [])

        if self.__class__.__name__ == "CrossviewForm" and data.get("published_only") is True:
            prefilters["animal_group__experiment__study__published"] = True

        return json.dumps(prefilters)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["prefilters"] = self.setPrefilters(cleaned_data)
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.createFields()
        self.setInitialValues()
        self.setFieldStyles()


class SummaryTextForm(forms.ModelForm):
    class Meta:
        model = models.SummaryText
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)


class SummaryTableForm(forms.ModelForm):
    class Meta:
        model = models.SummaryTable
        exclude = ("assessment", "table_type")
        field_classes = {"caption": QuillField}

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("parent", None)
        table_type = kwargs.pop("table_type", None)
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.instance = models.SummaryTable.build_default(self.assessment.id, table_type)
        # TODO - we shouldn't have to do this; and 400 errors are not rendering
        # instead, switch to htmx or use a REST API
        if self.initial:
            self.instance.title = self.initial["title"]
            self.instance.slug = self.initial["slug"]
            self.instance.content = self.initial["content"]
            self.instance.published = self.initial["published"]
            self.instance.caption = self.initial["caption"]

    def clean_slug(self):
        return check_unique_for_assessment(self, "slug")

    def clean_title(self):
        return check_unique_for_assessment(self, "title")


class SummaryTableSelectorForm(forms.Form):
    table_type = forms.IntegerField(widget=forms.Select(choices=constants.TableType.choices))

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("parent")
        _ = kwargs.pop("instance")
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        url = models.SummaryTable.get_list_url(self.assessment.id)
        return BaseFormHelper(
            self,
            legend_text="Select table type",
            help_text="""
            HAWC has a number of predefined table formats which are designed for different applications
            of the tool. Please select the table type you wish to create.
            """,
            submit_text="Create table",
            cancel_url=url,
        )


class SummaryTableModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.assessment}: [{obj.get_table_type_display()}] {obj}"


class SummaryTableCopySelectorForm(forms.Form):
    table = SummaryTableModelChoiceField(
        label="Summary table", queryset=models.Visual.objects.all()
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        self.cancel_url = kwargs.pop("cancel_url")
        self.assessment_id = kwargs.pop("assessment_id")
        self.queryset = kwargs.pop("queryset")
        super().__init__(*args, **kwargs)
        self.fields["table"].queryset = self.queryset

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"

        return BaseFormHelper(
            self,
            legend_text="Select summary table",
            help_text="""
                Select an existing summary table and copy as a new summary table. You will be taken to a new view to
                create a new table, but the form will be pre-populated using the values from
                the currently-selected table.
            """,
            submit_text="Copy table",
            cancel_url=self.cancel_url,
        )

    def get_create_url(self):
        table = self.cleaned_data["table"]
        return (
            reverse("summary:tables_create", args=(self.assessment_id, table.table_type))
            + f"?initial={table.pk}"
        )


class VisualForm(forms.ModelForm):
    class Meta:
        model = models.Visual
        exclude = ("assessment", "visual_type", "prefilters")

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        visual_type = kwargs.pop("visual_type", None)
        super().__init__(*args, **kwargs)
        if "settings" in self.fields:
            self.fields["settings"].widget.attrs["rows"] = 2
        if assessment:
            self.instance.assessment = assessment
        if visual_type is not None:  # required if value is 0
            self.instance.visual_type = visual_type
        if self.instance.visual_type not in [
            constants.VisualType.BIOASSAY_AGGREGATION,
            constants.VisualType.ROB_HEATMAP,
            constants.VisualType.LITERATURE_TAGTREE,
            constants.VisualType.EXTERNAL_SITE,
            constants.VisualType.EXPLORE_HEATMAP,
            constants.VisualType.PLOTLY,
        ]:
            self.fields["sort_order"].widget = forms.HiddenInput()

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": "Update an existing visualization.",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new visualization",
                "help_text": """
                    Create a custom-visualization.
                    Generally, you will select a subset of available data on the
                    "Data" tab, then will customize the visualization using the
                    "Settings" tab. To view a preview of the visual at any time,
                    select the "Preview" tab.
                """,
                "cancel_url": self.instance.get_list_url(self.instance.assessment_id),
            }

        helper = BaseFormHelper(self, **inputs)

        helper.form_id = "visualForm"
        return helper

    def clean_slug(self):
        return check_unique_for_assessment(self, "slug")

    def clean_title(self):
        return check_unique_for_assessment(self, "title")

    def clean_caption(self):
        caption = self.cleaned_data["caption"]
        validators.validate_hyperlinks(caption)
        return validators.clean_html(caption)


class VisualModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.assessment}: [{obj.get_visual_type_display()}] {obj}"


class VisualSelectorForm(forms.Form):
    visual = VisualModelChoiceField(label="Visualization", queryset=models.Visual.objects.all())

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        self.cancel_url = kwargs.pop("cancel_url")
        self.assessment_id = kwargs.pop("assessment_id")
        self.queryset = kwargs.pop("queryset")
        super().__init__(*args, **kwargs)
        self.fields["visual"].queryset = self.queryset

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"
        return BaseFormHelper(
            self,
            legend_text="Copy visualization",
            help_text="""
                Select an existing visualization from this assessment to copy as a template for a
                new one. This will include all model-settings, and the selected dataset.""",
            submit_text="Copy selected as new",
            cancel_url=self.cancel_url,
        )

    def get_create_url(self):
        visual = self.cleaned_data["visual"]
        return (
            reverse("summary:visualization_create", args=(self.assessment_id, visual.visual_type))
            + f"?initial={visual.pk}"
        )


class EndpointAggregationForm(VisualForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.setHelper()
        self.helper.attrs["novalidate"] = ""

    class Meta:
        model = models.Visual
        exclude = ("assessment", "visual_type", "prefilters", "studies", "sort_order")


class CrossviewForm(PrefilterMixin, VisualForm):
    prefilter_include = ("study", "bioassay", "effect_tags")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dose_units"].queryset = DoseUnits.objects.get_animal_units(
            self.instance.assessment
        )
        self.helper = self.setHelper()

    class Meta:
        model = models.Visual
        exclude = ("assessment", "visual_type", "endpoints", "studies")


class RoBForm(PrefilterMixin, VisualForm):
    prefilter_include = ("bioassay",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["studies"].queryset = self.fields["studies"].queryset.filter(
            assessment=self.instance.assessment
        )
        self.helper = self.setHelper()

    class Meta:
        model = models.Visual
        exclude = ("assessment", "visual_type", "dose_units", "endpoints")


class TagtreeForm(VisualForm):
    root_node = forms.TypedChoiceField(
        coerce=int,
        choices=[],
        label="Root node",
        help_text="Select the root node for the tag tree (the left-most node to be displayed)",
        required=True,
    )
    required_tags = forms.TypedMultipleChoiceField(
        coerce=int,
        choices=[],
        label="Filter references by tags",
        help_text="Filter which references are displayed by selecting required tags. If tags are selected, only references which have one or more of these tags (not including descendants) will be displayed.<br><br><i>This field is optional; if no tags are selected, all references will be displayed.</i>",
        required=False,
    )
    pruned_tags = forms.TypedMultipleChoiceField(
        coerce=int,
        choices=[],
        label="Hidden tags",
        help_text="Select tags which should be hidden from the tagtree. If a parent-tag is selected, all child-tags will also be hidden.<br><br><i>This field is optional; if no tags are selected, then all tags will be displayed.</i>",
        required=False,
    )
    hide_empty_tag_nodes = forms.BooleanField(
        label="Hide tags with no references",
        help_text="Prune tree; show only tags which contain at least one reference.",
        required=False,
    )
    width = forms.IntegerField(
        label="Width",
        initial=1280,
        min_value=500,
        max_value=2000,
        required=True,
        help_text="The width of the visual, in pixels.",
    )
    height = forms.IntegerField(
        label="Height",
        initial=800,
        min_value=500,
        max_value=3000,
        required=True,
        help_text="The height of the visual, in pixels. If you have overlapping nodes, add more height",
    )
    show_legend = forms.BooleanField(
        label="Show Legend",
        help_text="Describes what each node type indicates",
        initial=True,
        required=False,
    )
    show_counts = forms.BooleanField(
        label="Show Node Counts",
        help_text="Display the count for each node and scale size accordingly",
        initial=True,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.setHelper()
        self.helper.add_row("root_node", 3, "col-md-4")
        self.helper.add_row(
            "hide_empty_tag_nodes", 5, ["col-md-3", "col-md-2", "col-md-2", "col-md-3", "col-md-2"]
        )

        choices = [
            (tag.id, tag.get_nested_name())
            for tag in ReferenceFilterTag.get_assessment_qs(
                self.instance.assessment_id, include_root=True
            )
        ]
        self.fields["root_node"].choices = choices
        self.fields["required_tags"].choices = choices[1:]
        self.fields["pruned_tags"].choices = choices[1:]

        self.fields["required_tags"].widget.attrs.update(size=10)
        self.fields["pruned_tags"].widget.attrs.update(size=10)

        data = json.loads(self.instance.settings)
        if "root_node" in data:
            self.fields["root_node"].initial = data["root_node"]
        if "required_tags" in data:
            self.fields["required_tags"].initial = data["required_tags"]
        if "pruned_tags" in data:
            self.fields["pruned_tags"].initial = data["pruned_tags"]
        if "hide_empty_tag_nodes" in data:
            self.fields["hide_empty_tag_nodes"].initial = data["hide_empty_tag_nodes"]
        if "width" in data:
            self.fields["width"].initial = data["width"]
        if "height" in data:
            self.fields["height"].initial = data["height"]
        if "show_legend" in data:
            self.fields["show_legend"].initial = data["show_legend"]
        if "show_counts" in data:
            self.fields["show_counts"].initial = data["show_counts"]

    def save(self, commit=True):
        self.instance.settings = json.dumps(
            dict(
                root_node=self.cleaned_data["root_node"],
                required_tags=self.cleaned_data["required_tags"],
                pruned_tags=self.cleaned_data["pruned_tags"],
                hide_empty_tag_nodes=self.cleaned_data["hide_empty_tag_nodes"],
                width=self.cleaned_data["width"],
                height=self.cleaned_data["height"],
                show_legend=self.cleaned_data["show_legend"],
                show_counts=self.cleaned_data["show_counts"],
            )
        )
        return super().save(commit)

    class Meta:
        model = models.Visual
        fields = (
            "title",
            "slug",
            "caption",
            "published",
            "root_node",
            "required_tags",
            "pruned_tags",
            "hide_empty_tag_nodes",
            "width",
            "height",
            "show_legend",
            "show_counts",
        )


class ExternalSiteForm(VisualForm):
    external_url = forms.URLField(
        label="External URL",
        help_text="""
        <p class="form-text text-muted">
            Embed an external website. The following websites can be linked to:
        </p>
        <ul class="form-text text-muted">
            <li><a href="https://public.tableau.com/">Tableau (public)</a> - press the "share" icon and then select the URL in the "link" text box. For example, <code>https://public.tableau.com/shared/JWH9N8XGN</code>.</li>
        </ul>
        <p class="form-text text-muted">
            If you'd like to link to another website, please contact us.
        </p>
        """,
    )
    filters = forms.CharField(
        label="Data filters",
        initial="[]",
        validators=[validate_json_pydantic(constants.TableauFilterList)],
        help_text="""<p class="form-text text-muted">
        Data are expected to be in JSON format, where the each key is a filter name and value is a filter value.
        For more details, view the <a href="https://help.tableau.com/current/api/embedding_api/en-us/docs/embedding_api_filter.html">Tableau documentation</a>. For example: <code>[{"field": "Category", "value": "Technology"}, {"field": "State", "value": "North Carolina,Virginia"}]</code>. To remove filters, set string to <code>[]</code>.
        </p>""",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        data = json.loads(self.instance.settings)
        if "external_url" in data:
            self.fields["external_url"].initial = data["external_url"]
        if "filters" in data:
            self.fields["filters"].initial = json.dumps(data["filters"])

        self.helper = self.setHelper()

    def save(self, commit=True):
        self.instance.settings = json.dumps(
            dict(
                external_url=self.cleaned_data["external_url"],
                external_url_hostname=self.cleaned_data["external_url_hostname"],
                external_url_path=self.cleaned_data["external_url_path"],
                external_url_query_args=self.cleaned_data["external_url_query_args"],
                filters=json.loads(self.cleaned_data["filters"]),
            )
        )
        return super().save(commit)

    class Meta:
        model = models.Visual
        fields = (
            "title",
            "slug",
            "caption",
            "published",
        )

    DOMAIN_TABLEAU = "public.tableau.com"
    VALID_DOMAINS = {
        DOMAIN_TABLEAU,
    }

    def clean_external_url(self):
        external_url = self.cleaned_data.get("external_url")
        url = urlparse(external_url)

        # check allowlist
        if url.netloc not in self.VALID_DOMAINS:
            msg = f"{url.netloc} not on the list of accepted domains, please contact webmasters to request additions"
            raise forms.ValidationError(msg)

        external_url = urlunparse(("https", url.netloc, url.path, "", "", ""))
        external_url_hostname = urlunparse(("https", url.netloc, "", "", "", ""))

        if url.path == "" or url.path == "/":
            raise forms.ValidationError("A URL path must be specified.")

        external_url_query_args = []
        if url.netloc == self.DOMAIN_TABLEAU:
            external_url_query_args = [":showVizHome=no", ":embed=y"]

        self.cleaned_data.update(
            external_url=external_url,
            external_url_hostname=external_url_hostname,
            external_url_path=url.path,
            external_url_query_args=external_url_query_args,
        )

        return external_url


class ExploreHeatmapForm(VisualForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.setHelper()

    class Meta:
        model = models.Visual
        fields = (
            "title",
            "slug",
            "settings",
            "caption",
            "published",
        )


class PlotlyVisualForm(VisualForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["settings"].label = "JSON configuration"
        self.fields[
            "settings"
        ].help_text = f"""Create a {new_window_a("https://plotly.com/", "Plotly")} visual using Python or R, and then export the visual and display to JSON ({new_window_a("https://github.com/plotly/plotly.R/issues/590#issuecomment-220864613" ,"R")} or {new_window_a("https://plotly.github.io/plotly.py-docs/generated/plotly.io.to_json.html", "Python")})."""
        self.helper = self.setHelper()

    class Meta:
        model = models.Visual
        fields = (
            "title",
            "slug",
            "settings",
            "caption",
            "published",
        )

    def clean_settings(self):
        # we remove <extra> tag; by default it's included in plotly visuals but it doesn't pass
        # our html validation checks
        settings: str = (
            self.cleaned_data.get("settings", "")
            .strip()
            .replace("<extra>", "")
            .replace("</extra>", "")
        )
        try:
            json.loads(settings)
        except ValueError as err:
            raise forms.ValidationError("Invalid JSON format") from err
        if len(json.loads(settings)) == 0:
            raise forms.ValidationError("Settings cannot be empty")
        validate_html_tags(settings)
        validate_hyperlinks(settings)
        try:
            pio.from_json(settings)
        except ValueError as err:
            raise forms.ValidationError("Invalid Plotly figure") from err
        return settings


def get_visual_form(visual_type):
    try:
        return {
            constants.VisualType.BIOASSAY_AGGREGATION: EndpointAggregationForm,
            constants.VisualType.BIOASSAY_CROSSVIEW: CrossviewForm,
            constants.VisualType.ROB_HEATMAP: RoBForm,
            constants.VisualType.ROB_BARCHART: RoBForm,
            constants.VisualType.LITERATURE_TAGTREE: TagtreeForm,
            constants.VisualType.EXTERNAL_SITE: ExternalSiteForm,
            constants.VisualType.EXPLORE_HEATMAP: ExploreHeatmapForm,
            constants.VisualType.PLOTLY: PlotlyVisualForm,
        }[visual_type]
    except Exception:
        raise ValueError()


class DataPivotForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment
        self.helper = self.setHelper()
        self.fields["settings"].widget.attrs["rows"] = 2

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": "Update an existing data-pivot.",
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new data-pivot",
                "help_text": """
                    Create a custom-visualization for this assessment.
                    Generally, you will select a subset of available data, then
                    customize the visualization the next-page.
                """,
                "cancel_url": self.instance.get_list_url(self.instance.assessment_id),
            }

        helper = BaseFormHelper(self, **inputs)

        helper.form_id = "dataPivotForm"
        return helper

    def clean_slug(self):
        return check_unique_for_assessment(self, "slug")

    def clean_title(self):
        return check_unique_for_assessment(self, "title")

    def clean_caption(self):
        caption = self.cleaned_data["caption"]
        validators.validate_hyperlinks(caption)
        return validators.clean_html(caption)


class DataPivotUploadForm(DataPivotForm):
    class Meta:
        model = models.DataPivotUpload
        exclude = ("assessment",)

    def clean(self):
        cleaned_data = super().clean()
        excel_file = cleaned_data.get("excel_file")
        worksheet_name = cleaned_data.get("worksheet_name", "")

        if excel_file:
            # see if it loads
            try:
                wb = load_workbook(excel_file, read_only=True)
            except InvalidFileException:
                self.add_error(
                    "excel_file",
                    "Unable to read Excel file. Please upload an Excel file in XLSX format.",
                )
                return

            # check worksheet name
            if worksheet_name and worksheet_name not in wb.sheetnames:
                self.add_error("worksheet_name", f"Worksheet name {worksheet_name} not found.")
                return
            else:
                worksheet_name = wb.sheetnames[0]

            df = pd.read_excel(excel_file, sheet_name=worksheet_name)

            # check data
            if df.shape[0] < 2:
                self.add_error("excel_file", "Must contain at least 2 rows of data.")

            if df.shape[1] < 2:
                self.add_error("excel_file", "Must contain at least 2 columns.")


class DataPivotQueryForm1(DataPivotForm):
    class Meta:
        model = models.DataPivotQuery
        fields = (
            "title",
            "slug",
            "evidence_type",
            "export_style",
            "preferred_units",
            "settings",
            "caption",
            "published",
            "prefilters",
        )

    def _get_prefilter_form(self,data,**form_kwargs):
        prefix = form_kwargs.pop("prefix",None)
        #data = json.loads(data) # TODO migrate to json
        return self.prefilter(data=data,prefix=prefix,assessment=self.instance.assessment,form_kwargs=form_kwargs).form
    
    def __init__(self, *args, **kwargs):
        evidence_type = kwargs.pop("evidence_type",None)
        super().__init__(*args, **kwargs)

        if evidence_type is not None:
            self.instance.evidence_type = evidence_type
        self.fields["evidence_type"].initial = self.instance.evidence_type
        self.fields["evidence_type"].disabled = True

        self.prefilter = prefilters.Prefilter.from_study_type(self.instance.evidence_type,self.instance.assessment).value
        self.fields["prefilters"] = DynamicFormField(prefix="prefilters",form_class=self._get_prefilter_form,label="")
        self.fields["preferred_units"].required = False
        self.js_units_choices = json.dumps(
            [
                {"id": obj.id, "name": obj.name}
                for obj in DoseUnits.objects.get_animal_units(self.instance.assessment)
            ]
        )
        self.helper = self.setHelper()

    def save(self, commit=True):
        self.instance.preferred_units = self.cleaned_data.get("preferred_units", [])
        return super().save(commit=commit)

    def clean_export_style(self):
        evidence_type = self.cleaned_data["evidence_type"]
        export_style = self.cleaned_data["export_style"]
        if (
            evidence_type not in (constants.StudyType.IN_VITRO, constants.StudyType.BIOASSAY)
            and export_style != constants.ExportStyle.EXPORT_GROUP
        ):
            raise forms.ValidationError(
                "Outcome/Result level export not implemented for this data-type."
            )
        return export_style
            

class DataPivotQueryForm(PrefilterMixin, DataPivotForm):
    prefilter_include = ("study", "bioassay", "epi", "invitro", "eco", "effect_tags")

    class Meta:
        model = models.DataPivotQuery
        fields = (
            "title",
            "slug",
            "evidence_type",
            "export_style",
            "preferred_units",
            "settings",
            "caption",
            "published",
            "prefilters",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["evidence_type"].choices = (
            (constants.StudyType.BIOASSAY, "Animal Bioassay"),
            (constants.StudyType.EPI, "Epidemiology"),
            (constants.StudyType.EPI_META, "Epidemiology meta-analysis/pooled analysis"),
            (constants.StudyType.IN_VITRO, "In vitro"),
            (constants.StudyType.ECO, "Ecology"),
        )
        self.fields["preferred_units"].required = False
        self.js_units_choices = json.dumps(
            [
                {"id": obj.id, "name": obj.name}
                for obj in DoseUnits.objects.get_animal_units(self.instance.assessment)
            ]
        )
        self.helper = self.setHelper()

    def save(self, commit=True):
        self.instance.preferred_units = self.cleaned_data.get("preferred_units", [])
        return super().save(commit=commit)

    def clean_export_style(self):
        evidence_type = self.cleaned_data["evidence_type"]
        export_style = self.cleaned_data["export_style"]
        if (
            evidence_type not in (constants.StudyType.IN_VITRO, constants.StudyType.BIOASSAY)
            and export_style != constants.ExportStyle.EXPORT_GROUP
        ):
            raise forms.ValidationError(
                "Outcome/Result level export not implemented for this data-type."
            )
        return export_style


class DataPivotSettingsForm(forms.ModelForm):
    class Meta:
        model = models.DataPivot
        fields = ("settings",)


class DataPivotModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.assessment}: {obj}"


class DataPivotSelectorForm(forms.Form):
    dp = DataPivotModelChoiceField(
        label="Data Pivot", queryset=models.DataPivot.objects.all(), empty_label=None
    )

    reset_row_overrides = forms.BooleanField(
        help_text="Reset all row-level customization in the data-pivot copy",
        required=False,
        initial=True,
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance")
        user = kwargs.pop("user")
        self.cancel_url = kwargs.pop("cancel_url")
        super().__init__(*args, **kwargs)
        self.fields["dp"].queryset = models.DataPivot.objects.clonable_queryset(user)

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"

        return BaseFormHelper(
            self,
            legend_text="Copy data pivot",
            help_text="""
                Select an existing data pivot and copy as a new data pivot. This includes all
                model-settings, and the selected dataset. You will be taken to a new view to
                create a new data pivot, but the form will be pre-populated using the values from
                the currently-selected data pivot.""",
            submit_text="Copy selected as new",
            cancel_url=self.cancel_url,
        )


class SmartTagForm(forms.Form):
    RESOURCE_CHOICES = (
        ("study", "Study"),
        ("endpoint", "Endpoint"),
        ("visual", "Visualization"),
        ("data_pivot", "Data Pivot"),
    )
    resource = forms.ChoiceField(choices=RESOURCE_CHOICES)
    study = AutocompleteChoiceField(
        autocomplete_class=StudyAutocomplete,
        help_text="Type a few characters of the study name, then click to select.",
    )
    endpoint = AutocompleteChoiceField(
        autocomplete_class=EndpointAutocomplete,
        help_text="Type a few characters of the endpoint name, then click to select.",
    )
    visual = AutocompleteChoiceField(
        autocomplete_class=autocomplete.VisualAutocomplete,
        help_text="Type a few characters of the visual name, then click to select.",
    )
    data_pivot = AutocompleteChoiceField(
        autocomplete_class=autocomplete.DataPivotAutocomplete,
        help_text="Type a few characters of the data-pivot name, then click to select.",
    )

    def __init__(self, *args, **kwargs):
        assessment_id = kwargs.pop("assessment_id", -1)
        super().__init__(*args, **kwargs)
        self.fields["study"].set_filters({"assessment_id": assessment_id})
        self.fields["endpoint"].set_filters(
            {"animal_group__experiment__study__assessment_id": assessment_id}
        )
        self.fields["visual"].set_filters({"assessment_id": assessment_id})
        self.fields["data_pivot"].set_filters({"assessment_id": assessment_id})
