from django.core.mail import send_mail, mail_admins
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.contrib.contenttypes.models import ContentType

from selectable.forms import AutoCompleteWidget, AutoCompleteSelectMultipleWidget
from pagedown.widgets import PagedownWidget
from markdown_deux import markdown
from utils.forms import BaseFormHelper

from myuser.lookups import HAWCUserLookup

from . import models, lookups


class AssessmentForm(forms.ModelForm):

    class Meta:
        exclude = ('enable_literature_review',
                   'enable_project_management',
                   'enable_data_extraction',
                   'enable_risk_of_bias',
                   'enable_bmd',
                   'enable_summary_text')
        model = models.Assessment

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['project_manager'].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup)
        self.fields['team_members'].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup)
        self.fields['reviewers'].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup)

        self.helper = self.setHelper()

    def setHelper(self):
        # by default take-up the whole row-fluid
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3
                widget.attrs['class'] += " html5text"

        if self.instance.id:
            inputs = {
                "legend_text": "Update {}".format(self.instance),
                "help_text":   "Update an existing HAWC assessment.<br><br>* required fields",
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": "Create new assessment",
                "help_text":   """
                    Assessments are the fundamental objects in HAWC; all data added to the
                    tool will be related to an assessment. The settings below are used to
                    describe the basic characteristics of the assessment, along with setting
                    up permissions for role-based authorization and access for viewing and
                    editing content associated with an assessment.<br><br>* required fields""",
                "cancel_url": reverse_lazy('portal')
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 2, "span6")
        helper.add_fluid_row('version', 2, "span6")
        helper.add_fluid_row('project_manager', 3, "span4")
        helper.attrs['novalidate'] = ''
        return helper


class AssessmentModulesForm(forms.ModelForm):

    class Meta:
        fields = ('enable_literature_review',
                  'enable_data_extraction',
                  'enable_project_management',
                  'enable_risk_of_bias',
                  'enable_bmd',
                  'enable_summary_text')
        model = models.Assessment

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['enable_risk_of_bias'].label = f"Enable {self.instance.get_rob_name_display().lower()}"
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            "legend_text": "Update enabled modules",
            "help_text":   """
                HAWC is composed of multiple modules, each designed
                to capture data and decisions related to specific components of a
                health assessment. This screen allows a project-manager to change
                which modules are enabled for this assessment. Modules can be
                enabled or disabled at any time; content already entered into a particular
                module will not be changed when enabling or disabling modules.
                """,
            "cancel_url": self.instance.get_absolute_url()
        }
        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = models.Attachment
        exclude = ('content_type', 'object_id', 'content_object')

    def __init__(self, *args, **kwargs):
        obj = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        if obj:
            self.instance.content_type = ContentType.objects.get_for_model(obj)
            self.instance.object_id = obj.id
            self.instance.content_object = obj
        self.helper = self.setHelper()

    def setHelper(self):
        # by default take-up the whole row-fluid
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3
                widget.attrs['class'] += " html5text"

        if self.instance.id:
            inputs = {"legend_text": "Update {}".format(self.instance)}
        else:
            inputs = {"legend_text": "Create new attachment"}
        inputs["cancel_url"] = self.instance.get_absolute_url()

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper


class SpeciesForm(forms.ModelForm):

    class Meta:
        model = models.Species
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        return self.cleaned_data['name'].title()


class StrainForm(forms.ModelForm):

    class Meta:
        model = models.Strain
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        return self.cleaned_data['name'].title()


class DoseUnitsForm(forms.ModelForm):

    class Meta:
        model = models.DoseUnits
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = AutoCompleteWidget(
            lookup_class=lookups.DoseUnitsLookup,
            allow_new=True)
        for fld in list(self.fields.keys()):
            self.fields[fld].widget.attrs['class'] = 'span12'


class EffectTagForm(forms.ModelForm):

    class Meta:
        model = models.EffectTag
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        kwargs.pop('parent')
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = AutoCompleteWidget(
            lookup_class=lookups.EffectTagLookup,
            allow_new=True)
        for fld in list(self.fields.keys()):
            self.fields[fld].widget.attrs['class'] = 'span12'


class AssessmentEmailManagersForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=PagedownWidget())

    def send_email(self):
        from_email = settings.DEFAULT_FROM_EMAIL
        subject = "[HAWC] {0}" .format(self.cleaned_data['subject'])
        message = ""
        recipient_list = self.assessment.get_project_manager_emails()
        html_message = markdown(self.cleaned_data['message'])
        send_mail(subject, message, from_email, recipient_list,
                  html_message=html_message,
                  fail_silently=False)

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop('assessment', None)
        super().__init__(*args, **kwargs)
        for key in list(self.fields.keys()):
            self.fields[key].widget.attrs['class'] = 'span12'


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        subject = '[HAWC contact us]: {}'.format(self.cleaned_data['subject'])
        content = '{0}\n\n{1}\n{2}'.format(
            self.cleaned_data['message'],
            self.cleaned_data['name'],
            self.cleaned_data['email']
        )
        mail_admins(subject, content, fail_silently=False)

    def __init__(self, *args, **kwargs):
        self.back_href = kwargs.pop('back_href', None)
        super().__init__(*args, **kwargs)
        self.helper = self.setHelper()

    def setHelper(self):
        # by default take-up the whole row-fluid
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

        inputs = {
            "legend_text": "Contact HAWC developers",
            "help_text": """
                Have a question, comment, or need some help?
                Use this form to to let us know what's going on.
            """,
            "cancel_url": self.back_href

        }
        helper = BaseFormHelper(self, **inputs)
        helper.form_class = "loginForm"
        return helper
