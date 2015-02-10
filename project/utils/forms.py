from django import forms

from crispy_forms import helper as cf
from crispy_forms import layout as cfl
from crispy_forms import bootstrap as cfb


class BaseFormHelper(cf.FormHelper):

    form_class = 'form-horizontal'
    error_text_inline = False

    def __init__(self, form=None, **kwargs):
        self.attrs = {}
        self.inputs = []
        self.kwargs = kwargs

        if form:
            self.form = form
            self.layout = self.build_default_layout(form)

    def build_default_layout(self, form):
        layout = cfl.Layout(*form.fields.keys())

        if self.kwargs.get('legend_text'):
            layout.insert(0, cfl.HTML(u"<legend>{}</legend>".format(self.kwargs.get('legend_text'))))

        if self.kwargs.get('help_text'):
            layout.insert(1, cfl.HTML("""<p class="help-block">{}</p><br>""".format(self.kwargs.get('help_text'))))

        if self.kwargs.get('cancel_url'):
            layout.append(
                cfb.FormActions(
                    cfl.Submit('save', 'Save'),
                    cfl.HTML("""<a role="button" class="btn btn-default" href="{}">Cancel</a>""".format(self.kwargs.get('cancel_url'))),
            ))

        return layout

    def add_adder(self, cls, title, url):
        """
        Add a "plus" button to add a new creator item in a new window.
        """
        self.layout.append(
            cfl.HTML("""<a class="btn btn-primary adders {}"
                           title="{}" href="{}"
                           onclick="return HAWCUtils.newWindowPopupLink(this);">
                                <i class="icon-plus icon-white"></i></a>""".format(
            cls, title, url)))

    def add_fluid_row(self, firstField, numFields, wrapperClasses):
        first = self.layout.index(firstField)
        if type(wrapperClasses) in [str, unicode]:
            wrapperClasses = [wrapperClasses]*numFields
        for i, v in enumerate(wrapperClasses):
            self[first+i].wrap(cfl.Field, wrapper_class=v)
        self[first:first+numFields].wrap_together(cfl.Div, css_class="row-fluid")


def form_error_list_to_ul(form):
    #Convert a list of errors from a form into a ul, used for endpoint group
    # since everything is controlled by AJAX and JSON
    txt = ['<ul>']
    for key, values in form.errors.iteritems():
        for value in values:
            if key == '__all__':
                txt.append("<li>" + value + "</li>")
            else:
                txt.append("<li>" + key + ": " + value + "</li>")
    txt.append('</ul>')
    return ' '.join(txt)


class FormsetWithIgnoredFields(forms.BaseModelFormSet):

    ignored_fields = []   # list of field names to be ignored

    def __init__(self, *args, **kwargs):
        super(FormsetWithIgnoredFields, self).__init__(*args, **kwargs)

        for i, form in enumerate(self.forms):
            for field_name in self.ignored_fields:
                value = self.data.get('form-{0}-{1}'.format(i, field_name))
                if value:
                    form.fields[field_name].initial = value


def remove_holddown_helptext(form, fields):
    """
    Removes "Hold down the...." help-text for specified form fields.
    https://djangosnippets.org/snippets/2400/
    """
    remove_message = u'Hold down "Control", or "Command" on a Mac, to select more than one.'
    for field in fields:
        if field in form.base_fields:
            if form.base_fields[field].help_text:
                form.base_fields[field].help_text = form.base_fields[field].help_text.replace(remove_message, '').strip()
    return form
