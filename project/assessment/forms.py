from django.core.mail import send_mail, mail_admins
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse_lazy

from selectable.forms import AutoCompleteWidget, AutoCompleteSelectMultipleWidget
from pagedown.widgets import PagedownWidget
from markdown_deux import markdown
from utils.forms import BaseFormHelper, remove_holddown

from myuser.lookups import HAWCUserLookup

from . import models, lookups


class AssessmentForm(forms.ModelForm):

    class Meta:
        exclude = ('enable_literature_review',
                   'enable_data_extraction',
                   'enable_study_quality',
                   'enable_bmd',
                   'enable_reference_values',
                   'enable_summary_text',
                   'enable_comments')
        model = models.Assessment

    def __init__(self, *args, **kwargs):
        super(AssessmentForm, self).__init__(*args, **kwargs)

        self.fields['project_manager'].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup)
        self.fields['team_members'].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup)
        self.fields['reviewers'].widget = AutoCompleteSelectMultipleWidget(
            lookup_class=HAWCUserLookup)

        remove_holddown(self, ('project_manager', 'team_members', 'reviewers'))

        self.helper = self.setHelper()

    def setHelper(self):
        # by default take-up the whole row-fluid
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   u"Update an existing HAWC assessment.<br><br>* required fields",
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new assessment",
                "help_text":   u"""
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
        return helper


class AssessmentModulesForm(forms.ModelForm):

    class Meta:
        fields = ('enable_literature_review',
                  'enable_data_extraction',
                  'enable_study_quality',
                  'enable_bmd',
                  'enable_reference_values',
                  'enable_summary_text',
                  'enable_comments')
        model = models.Assessment


class EffectTagForm(forms.ModelForm):

    class Meta:
        model = models.EffectTag

    def __init__(self, *args, **kwargs):
        kwargs.pop('parent')
        super(EffectTagForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = AutoCompleteWidget(
            lookup_class=lookups.EffectTagLookup,
            allow_new=True)
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span12'


class ReportTemplateForm(forms.ModelForm):

    class Meta:
        model = models.ReportTemplate
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        super(ReportTemplateForm, self).__init__(*args, **kwargs)

        for fld in ('description', 'report_type'):
            self.fields[fld].widget.attrs['class'] = 'span12'

        if parent:
            self.instance.assessment = parent


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
        super(AssessmentEmailManagersForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['class'] = 'span12'


class ContactForm(forms.Form):
    sender = forms.EmailField(label="Your email")
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        mail_admins(u'[Contact Us]: ' + self.cleaned_data['subject'],
                    self.cleaned_data['message'] + u'\n\n ' + self.cleaned_data['sender'],
                    fail_silently=False)

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs['class'] = 'span12'
