from django import forms

from crispy_forms import helper as cf
from crispy_forms import layout as cfl
from crispy_forms import bootstrap as cfb
from crispy_forms.utils import flatatt, TEMPLATE_PACK

from django.template.loader import render_to_string

from selectable import forms as selectable

from . import validators


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
        layout = cfl.Layout(*list(form.fields.keys()))

        if self.kwargs.get('legend_text'):
            layout.insert(0, cfl.HTML("<legend>{}</legend>".format(
                self.kwargs.get('legend_text'))))

        if self.kwargs.get('help_text'):
            layout.insert(1, cfl.HTML("""<p class="help-block">{}</p><br>""".format(
                self.kwargs.get('help_text'))))

        if self.kwargs.get('pdf_link'):
            self.addCustomFormActions(layout, [
                cfl.HTML("""<p><a class="btn btn-mini btn-primary" target="_blank" href="https://hero.epa.gov/hero/index.cfm/reference/downloads/reference_id/{}">Full text link <i className="fa fa-fw fa-file-pdf-o"></i></a><span>&nbsp;</span></p>""".format(
                    self.kwargs.get('pdf_link')))
            ])

        if self.kwargs.get('cancel_url'):
            self.addCustomFormActions(layout, [
                cfl.Submit('save', 'Save'),
                cfl.HTML("""<a role="button" class="btn btn-default" href="{}">Cancel</a>""".format(
                    self.kwargs.get('cancel_url')))
            ])

        if self.kwargs.get('form_actions'):
            self.addCustomFormActions(layout, self.kwargs.get('form_actions'))

        return layout

    @classmethod
    def addCustomFormActions(cls, layout, items):
        layout.append(cfb.FormActions(*items))

    def addBtnLayout(self, lst, idx, url, title, wrapper_class):
        """
        Render field plus an "add new" button to the right.
        """
        if type(lst[idx]) is str:
            fields = [lst[idx]]
        else:
            fields = lst[idx].fields
        lst[idx] = AdderLayout(
                *fields, adderURL=url, adderTitle=title,
                wrapper_class=wrapper_class)

    def add_fluid_row(self, firstField, numFields, wrapperClasses):
        first = self.layout.index(firstField)
        if type(wrapperClasses) in [str, str]:
            wrapperClasses = [wrapperClasses]*numFields
        for i, v in enumerate(wrapperClasses):
            self[first+i].wrap(cfl.Field, wrapper_class=v)
        self[first:first+numFields].wrap_together(cfl.Div, css_class="row-fluid")

    def add_td(self, firstField, numFields):
        first = self.layout.index(firstField)
        self[first:first+numFields].wrap_together(TdLayout)

    def add_header(self, firstField, text):
        self.layout.insert(
            self.layout.index(firstField),
            cfl.HTML("""<h4>{0}</h4>""".format(text)))


class CopyAsNewSelectorForm(forms.Form):
    label = None
    lookup_class = None

    def __init__(self, *args, **kwargs):
        parent_id = kwargs.pop('parent_id')
        super(CopyAsNewSelectorForm, self).__init__(*args, **kwargs)
        self.setupSelector(parent_id)

    def setupSelector(self, parent_id):
        fld = selectable.AutoCompleteSelectField(
            lookup_class=self.lookup_class,
            allow_new=False,
            label=self.label,
            widget=selectable.AutoComboboxSelectWidget)
        fld.widget.update_query_parameters({'related': parent_id})
        fld.widget.attrs['class'] = 'span11'
        self.fields['selector'] = fld


def form_error_list_to_lis(form):
    # Convert a list of errors from a form into a list of li,
    # used for endpoint group since everything is controlled by AJAX and JSON
    lis = []
    for key, values in form.errors.items():
        for value in values:
            if key == '__all__':
                lis.append("<li>" + value + "</li>")
            else:
                lis.append("<li>" + key + ": " + value + "</li>")
    return lis


def form_error_lis_to_ul(lis):
    return "<ul>{0}</ul>".format("".join(lis))


def addPopupLink(href, text):
    return """<a href="{0}"
                 onclick="return HAWCUtils.newWindowPopupLink(this);")>{1}</a>""".format(href, text)


class TdLayout(cfl.LayoutObject):
    """
    Layout object. It wraps fields in a <td>
    """
    template = "crispy_forms/layout/td.html"

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)
        self.css_class = kwargs.pop('css_class', '')
        self.css_id = kwargs.pop('css_id', None)
        self.template = kwargs.pop('template', self.template)
        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, **kwargs):
        fields = self.get_rendered_fields(form, form_style, context, **kwargs)
        return render_to_string(
            self.template,
            {'td': self, 'fields': fields, 'form_style': form_style}
        )


class AdderLayout(cfl.Field):
    """
    Adder layout object. It contains a link-button to add a new field.
    """
    template = "crispy_forms/layout/inputAdder.html"

    def __init__(self, *args, **kwargs):
        self.adderURL = kwargs.pop('adderURL', '')
        self.adderTitle = kwargs.pop('adderTitle', '')
        super(AdderLayout, self).__init__(*args, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        if extra_context is None:
            extra_context = {}
        extra_context["adderURL"] = self.adderURL
        extra_context["adderTitle"] = self.adderTitle
        return super(AdderLayout, self).render(form, form_style, context,
                                               template_pack, extra_context,
                                               **kwargs)


class CustomURLField(forms.URLField):
    default_validators = [validators.CustomURLValidator()]
