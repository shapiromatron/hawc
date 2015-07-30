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
            self.addCustomFormActions(layout, [
                cfl.Submit('save', 'Save'),
                cfl.HTML("""<a role="button" class="btn btn-default" href="{}">Cancel</a>""".format(self.kwargs.get('cancel_url')))
            ])

        if self.kwargs.get('form_actions'):
            self.addCustomFormActions(layout, self.kwargs.get('form_actions'))

        return layout

    @classmethod
    def addCustomFormActions(cls, layout, items):
        layout.append(cfb.FormActions(*items))

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


def form_error_list_to_lis(form):
    # Convert a list of errors from a form into a list of li,
    # used for endpoint group since everything is controlled by AJAX and JSON
    lis = []
    for key, values in form.errors.iteritems():
        for value in values:
            if key == '__all__':
                lis.append("<li>" + value + "</li>")
            else:
                lis.append("<li>" + key + ": " + value + "</li>")
    return lis


def form_error_lis_to_ul(lis):
    return u"<ul>{0}</ul>".format("".join(lis))


def anyNull(dict, fields):
    for field in fields:
        if dict.get(field) is None:
            return True
    return False


class FormsetWithIgnoredFields(forms.BaseModelFormSet):

    ignored_fields = []   # list of field names to be ignored

    def __init__(self, *args, **kwargs):
        super(FormsetWithIgnoredFields, self).__init__(*args, **kwargs)

        for i, form in enumerate(self.forms):
            for field_name in self.ignored_fields:
                value = self.data.get('form-{0}-{1}'.format(i, field_name))
                if value:
                    form.fields[field_name].initial = value
