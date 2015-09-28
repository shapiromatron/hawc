from django import forms
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.utils.functional import curry

from selectable import forms as selectable

from utils.forms import BaseFormHelper
from epi2.lookups import AdjustmentFactorLookup, CriteriaLookup

from . import models, lookups


class MetaProtocolForm(forms.ModelForm):

    CREATE_LEGEND = u"Create a new meta-protocol"

    CREATE_HELP_TEXT = u"""
        Create a new meta-protocol for an epidemiological
        assessment. A meta-protocol contains the methodology behind a
        meta-analysis or pooled analysis, which are frequently used
        techniques used to quantitatively summarize results from
        multiple studies or reference populations.
    """

    UPDATE_HELP_TEXT = u"Update an existing meta-protocol"

    inclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=CriteriaLookup,
        required=False)

    exclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=CriteriaLookup,
        required=False)

    CRITERION_FIELDS = [
        "inclusion_criteria",
        "exclusion_criteria",
    ]

    class Meta:
        model = models.MetaProtocol
        exclude = ('study', )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        super(MetaProtocolForm, self).__init__(*args, **kwargs)
        if parent:
            self.instance.study = parent
        self.fields['inclusion_criteria'].widget.update_query_parameters(
            {'related': self.instance.study.assessment_id})
        self.fields['exclusion_criteria'].widget.update_query_parameters(
            {'related': self.instance.study.assessment_id})
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld in self.CRITERION_FIELDS:
                    widget.attrs['class'] = 'span10'
                else:
                    widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   self.UPDATE_HELP_TEXT,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text":   self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.study.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 2, "span6")
        helper.add_fluid_row('lit_search_strategy', 2, "span6")
        helper.add_fluid_row('lit_search_start_date', 3, "span4")
        helper.add_fluid_row('inclusion_criteria', 2, "span6")

        url = reverse('epi2:studycriteria_create',
                      kwargs={'pk': self.instance.study.assessment.pk})
        helper.addBtnLayout(helper.layout[5], 0, url, "Create criteria", "span6")
        helper.addBtnLayout(helper.layout[5], 1, url, "Create criteria", "span6")

        return helper


class MetaResultForm(forms.ModelForm):

    CREATE_LEGEND = u"Create a new meta-result"

    CREATE_HELP_TEXT = u"""
        Create a new meta-result for an epidemiological assessment.
        A meta-result is the aggregate result from a meta-analysis or
        pooled analysis from multiple primary literature components.
    """

    UPDATE_HELP_TEXT = u"Update an existing meta-result"

    adjustment_factors = selectable.AutoCompleteSelectMultipleField(
        help_text="All factors which were included in final model",
        lookup_class=AdjustmentFactorLookup,
        required=False)

    class Meta:
        model = models.MetaResult
        exclude = ('protocol', )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        assessment = kwargs.pop('assessment', None)
        super(MetaResultForm, self).__init__(*args, **kwargs)

        self.fields['health_outcome'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.MetaResultHealthOutcomeLookup,
            allow_new=True)

        self.fields['exposure_name'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.MetaResultExposureNameLookup,
            allow_new=True)

        if parent:
            self.instance.protocol = parent

        self.fields['adjustment_factors'].widget.update_query_parameters(
                {'related': assessment.id})
        self.fields['health_outcome'].widget.update_query_parameters(
                {'related': assessment.id})
        self.fields['exposure_name'].widget.update_query_parameters(
                {'related': assessment.id})
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld == "adjustment_factors":
                    widget.attrs['class'] = 'span10'
                else:
                    widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   self.UPDATE_HELP_TEXT,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text":   self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.protocol.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('label', 2, "span6")
        helper.add_fluid_row('health_outcome', 2, "span6")
        helper.add_fluid_row('exposure_name', 2, "span6")
        helper.add_fluid_row('number_studies', 3, "span4")
        helper.add_fluid_row('n', 3, "span4")
        helper.add_fluid_row('lower_ci', 3, "span4")
        helper.add_fluid_row('adjustment_factors', 2, "span6")

        url = reverse(
            'epi2:adjustmentfactor_create',
            kwargs={'pk': self.instance.protocol.study.assessment.pk}
        )
        helper.addBtnLayout(helper.layout[8], 0, url, "Create criteria", "span6")

        return helper


class SingleResultForm(forms.ModelForm):

    class Meta:
        model = models.SingleResult
        fields = ('study', 'exposure_name', 'weight',
                  'n', 'estimate', 'lower_ci',
                  'upper_ci', 'ci_units', 'notes')

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super(SingleResultForm, self).__init__(*args, **kwargs)

        if parent:
            self.instance.meta_result = parent

        self.fields['study'].queryset = self.fields['study'].queryset\
            .filter(assessment=assessment, study_type=1)

        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        self.fields['study'].widget.attrs["class"] += " studySearch"

        helper = BaseFormHelper(self)
        helper.form_class = None
        return helper


class BaseSingleResultFormset(forms.BaseModelFormSet):

    def __init__(self, **kwargs):
        assessment = kwargs.pop('assessment')
        super(BaseSingleResultFormset, self).__init__(**kwargs)
        self.form = curry(self.form, assessment=assessment)


SingleResultFormset = modelformset_factory(
    models.SingleResult,
    can_delete=True,
    form=SingleResultForm,
    formset=BaseSingleResultFormset,
    extra=1)


class MetaResultSelectorForm(forms.Form):

    selector = selectable.AutoCompleteSelectField(
        lookup_class=lookups.MetaResultByStudyLookup,
        label='Meta Result',
        widget=selectable.AutoComboboxSelectWidget)

    def __init__(self, *args, **kwargs):
        study_id = kwargs.pop("study_id")
        super(MetaResultSelectorForm, self).__init__(*args, **kwargs)
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span11'
        self.fields['selector'].widget.update_query_parameters(
            {'related': study_id})
