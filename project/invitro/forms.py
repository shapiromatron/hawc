from django import forms
from django.core.urlresolvers import reverse
from selectable import forms as selectable

from assessment.lookups import EffectTagLookup
from utils.forms import BaseFormHelper

from . import models


class IVExperimentForm(forms.ModelForm):

    HELP_TEXT_CREATE = ""
    HELP_TEXT_UPDATE = "Update an existing experiment."

    class Meta:
        model = models.IVExperiment
        exclude = ('study', )

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('parent', None)
        super(IVExperimentForm, self).__init__(*args, **kwargs)
        if study:
            self.instance.study = study
        self.fields['cell_type'].queryset = \
            self.fields['cell_type'].queryset\
                .filter(study=self.instance.study)
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                'legend_text': u'Update {}'.format(self.instance),
                'help_text': self.HELP_TEXT_UPDATE,
                'cancel_url': self.instance.get_absolute_url()
            }
        else:
            inputs = {
                'legend_text': u'Create new experiment',
                'help_text': self.HELP_TEXT_CREATE,
                'cancel_url': self.instance.study.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 2, 'span6')
        helper.add_fluid_row('transfection', 2, 'span6')
        helper.add_fluid_row('dosing_notes', 2, 'span6')
        helper.add_fluid_row('has_positive_control', 2, 'span6')
        helper.add_fluid_row('has_negative_control', 2, 'span6')
        helper.add_fluid_row('has_vehicle_control', 2, 'span6')
        helper.add_fluid_row('control_notes', 2, 'span6')

        return helper


class IVEndpointForm(forms.ModelForm):

    HELP_TEXT_CREATE = ""
    HELP_TEXT_UPDATE = "Update an existing endpoint."

    class Meta:
        model = models.IVEndpoint
        exclude = (
            'assessment', 'experiment', 'additional_fields',
            'LOEL', 'NOEL',  # todo: temporary; adds back in
        )

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop('parent', None)
        assessment = kwargs.pop('assessment', None)
        super(IVEndpointForm, self).__init__(*args, **kwargs)
        if experiment:
            self.instance.experiment = experiment
        if assessment:
            self.instance.assessment = assessment

        self.fields['effects'].widget = selectable.AutoCompleteSelectMultipleWidget(
            lookup_class=EffectTagLookup)
        self.fields['effects'].help_text = 'Tags used to help categorize effect description.'

        self.fields['chemical'].queryset = \
            self.fields['chemical'].queryset\
                .filter(study=self.instance.experiment.study)

        self.fields['category'].queryset = \
            self.fields['category'].queryset.model\
                .get_root(self.instance.assessment_id).get_descendants()

        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld in ['effects']:
                    widget.attrs['class'] = 'span10'
                else:
                    widget.attrs['class'] = 'span12'

            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                'legend_text': u'Update {}'.format(self.instance),
                'help_text': self.HELP_TEXT_UPDATE,
                'cancel_url': self.instance.get_absolute_url()
            }
        else:
            inputs = {
                'legend_text': u'Create new endpoint',
                'help_text': self.HELP_TEXT_CREATE,
                'cancel_url': self.instance.study.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 2, 'span6')
        helper.add_fluid_row('chemical', 2, 'span6')
        helper.add_fluid_row('assay_type', 2, 'span6')
        helper.add_fluid_row('effect', 2, 'span6')
        helper.add_fluid_row('data_type', 4, 'span3')
        helper.add_fluid_row('observation_time', 2, 'span6')
        helper.add_fluid_row('monotonicity', 3, 'span4')
        helper.add_fluid_row('trend_test', 2, 'span6')
        helper.add_fluid_row('endpoint_notes', 2, 'span6')

        url = reverse(
            'assessment:effect_tag_create',
            kwargs={'pk': self.instance.assessment_id}
        )
        helper.addBtnLayout(helper.layout[2], 1, url, 'Add new effect tag', 'span6')

        return helper
