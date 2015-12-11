from django import forms

from utils.forms import BaseFormHelper

from . import models


class IVExperimentForm(forms.ModelForm):

    HELP_TEXT_CREATE = """"""
    HELP_TEXT_UPDATE = """Update an existing experiment."""

    class Meta:
        model = models.IVExperiment
        exclude = tuple()

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
                if fld in ["metric_units"]:
                    widget.attrs['class'] = 'span10'
                else:
                    widget.attrs['class'] = 'span12'

            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new experiment",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None

        return helper
