from django import forms

from hawc.apps.common.forms import BaseFormHelper

from ..common import selectable
from . import lookups, models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study design"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update an existing study design."

    class Meta:
        exclude = ("study",)
        model = models.Design
        widgets = {
            "country": selectable.AutoCompleteSelectMultipleWidget(
                lookup_class=lookups.CountryLookup
            ),
            "state": selectable.AutoCompleteSelectMultipleWidget(lookup_class=lookups.StateLookup),
            "ecoregion": selectable.AutoCompleteSelectMultipleWidget(
                lookup_class=lookups.EcoregionLookup
            ),
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        for fld in ("habitat_as_reported", "climate_as_reported"):
            self.fields[fld].widget.attrs["class"] = "html5text"
            self.fields[fld].widget.attrs["rows"] = 3

        if self.instance.id:
            helper = BaseFormHelper(self)
            helper.form_tag = False

        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text": self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.study.get_absolute_url(),
                "submit_text": "Next",
            }
            helper = BaseFormHelper(self, **inputs)

        helper.add_row("name", 3, "col-md-4")
        helper.add_row("country", 3, "col-md-4")
        helper.add_row("habitat", 4, "col-md-3")
        return helper


class CauseForm(forms.ModelForm):

    term = selectable.AutoCompleteSelectField(
        label="Cause Term",
        lookup_class=lookups.NestedTermLookup,
        required=False,
    )

    class Meta:
        exclude = ("study",)
        model = models.Cause

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.study = design.study

    @property
    def helper(self):
        for fld in ("comment", "as_reported"):
            self.fields[fld].widget.attrs["class"] = "html5text"
            self.fields[fld].widget.attrs["rows"] = 3
        self.fields["measure_detail"].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 6, "col-md-2")
        helper.add_row("level", 6, "col-md-2")
        helper.add_row("comment", 2, "col-md-6")
        return helper


class EffectForm(forms.ModelForm):

    term = selectable.AutoCompleteSelectField(
        label="Effect Term",
        lookup_class=lookups.NestedTermLookup,
        required=False,
    )

    class Meta:
        exclude = ("study",)
        model = models.Effect

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.study = design.study

    @property
    def helper(self):
        for fld in ("comment", "as_reported"):
            self.fields[fld].widget.attrs["class"] = "html5text"
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 3, "col-md-4")
        helper.add_row("measure_detail", 3, "col-md-4")
        helper.add_row("bio_org", 3, "col-md-4")
        return helper


class ResultForm(forms.ModelForm):

    cause = selectable.AutoCompleteSelectWidget(lookup_class=lookups.RelatedCauseLookup)

    effect = selectable.AutoCompleteSelectWidget(lookup_class=lookups.RelatedEffectLookup)

    class Meta:
        exclude = ("design",)
        model = models.Result

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.fields["cause"].required = True
        self.fields["effect"].required = True
        if design:
            self.instance.design = design

    @property
    def helper(self):
        for fld in ("relationship_comment", "modifying_factors_comment", "description"):
            self.fields[fld].widget.attrs["class"] = "html5text"
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("cause", 6, "col-md-2")
        helper.add_row("modifying_factors_comment", 6, "col-md-2")
        helper.add_row("low_variability", 5, "col-md-2")
        return helper
