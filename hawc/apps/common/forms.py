from crispy_forms import bootstrap as cfb
from crispy_forms import helper as cf
from crispy_forms import layout as cfl
from crispy_forms.utils import TEMPLATE_PACK, flatatt
from django import forms
from django.template.loader import render_to_string
from selectable import forms as selectable

from . import validators


class BaseFormHelper(cf.FormHelper):

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

        if self.kwargs.get("legend_text"):
            layout.insert(
                0, cfl.HTML(f"<legend>{self.kwargs.get('legend_text')}</legend>"),
            )

        if "help_text" in self.kwargs:
            layout.insert(
                1, cfl.HTML(f'<p class="help-block">{self.kwargs["help_text"]}</p><br>'),
            )

        if "cancel_url" in self.kwargs:
            self.addCustomFormActions(
                layout,
                [
                    cfl.Submit("save", "Save"),
                    cfl.HTML(
                        f'<a role="button" class="btn btn-light" href="{self.kwargs["cancel_url"]}">Cancel</a>'
                    ),
                ],
            )

        if self.kwargs.get("form_actions"):
            self.addCustomFormActions(layout, self.kwargs.get("form_actions"))

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
        lst[idx] = AdderLayout(*fields, adderURL=url, adderTitle=title, wrapper_class=wrapper_class)

    def add_row(self, firstField, numFields, wrapperClasses):
        first = self.layout.index(firstField)
        if type(wrapperClasses) in [str, str]:
            wrapperClasses = [wrapperClasses] * numFields
        for i, v in enumerate(wrapperClasses):
            self[first + i].wrap(cfl.Field, wrapper_class=v)
        self[first : first + numFields].wrap_together(
            cfl.Div, css_class="form-row", id=f"fluid_id_{firstField}_{numFields}"
        )

    def add_td(self, firstField, numFields):
        first = self.layout.index(firstField)
        self[first : first + numFields].wrap_together(TdLayout)

    def add_header(self, firstField, text):
        self.layout.insert(self.layout.index(firstField), cfl.HTML(f"<h4>{text}</h4>"))

    def find_layout_idx_for_field_name(self, field_name):
        idx = 0
        for el in self.layout:
            if isinstance(el, cfl.LayoutObject):
                for field_names in el.get_field_names():
                    if isinstance(field_names, list) and len(field_names) > 1:
                        if field_names[1] == field_name:
                            return idx
            elif isinstance(el, str):
                if el == field_name:
                    return idx
            idx += 1
        raise ValueError(f"Field not found: {field_name}")


class CopyAsNewSelectorForm(forms.Form):
    label = None
    lookup_class = None

    def __init__(self, *args, **kwargs):
        parent_id = kwargs.pop("parent_id")
        super(CopyAsNewSelectorForm, self).__init__(*args, **kwargs)
        self.setupSelector(parent_id)

    def setupSelector(self, parent_id):
        fld = selectable.AutoCompleteSelectField(
            lookup_class=self.lookup_class,
            allow_new=False,
            label=self.label,
            widget=selectable.AutoComboboxSelectWidget,
        )
        fld.widget.update_query_parameters({"related": parent_id})
        fld.widget.attrs["class"] = "col-md-11"
        self.fields["selector"] = fld


def form_error_list_to_lis(form):
    # Convert a list of errors from a form into a list of li,
    # used for endpoint group since everything is controlled by AJAX and JSON
    lis = []
    for key, values in form.errors.items():
        for value in values:
            if key == "__all__":
                lis.append("<li>" + value + "</li>")
            else:
                lis.append("<li>" + key + ": " + value + "</li>")
    return lis


def form_error_lis_to_ul(lis):
    return f"<ul>{''.join(lis)}</ul>"


def addPopupLink(href, text):
    return f'<a href="{href}" onclick="return HAWCUtils.newWindowPopupLink(this);")>{text}</a>'


class TdLayout(cfl.LayoutObject):
    """
    Layout object. It wraps fields in a <td>
    """

    template = "crispy_forms/layout/td.html"

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)
        self.css_class = kwargs.pop("css_class", "")
        self.css_id = kwargs.pop("css_id", None)
        self.template = kwargs.pop("template", self.template)
        self.flat_attrs = flatatt(kwargs)

    def render(self, form, form_style, context, **kwargs):
        fields = self.get_rendered_fields(form, form_style, context, **kwargs)
        return render_to_string(
            self.template, {"td": self, "fields": fields, "form_style": form_style}
        )


class AdderLayout(cfl.Field):
    """
    Adder layout object. It contains a link-button to add a new field.
    """

    template = "crispy_forms/layout/inputAdder.html"

    def __init__(self, *args, **kwargs):
        self.adderURL = kwargs.pop("adderURL", "")
        self.adderTitle = kwargs.pop("adderTitle", "")
        super(AdderLayout, self).__init__(*args, **kwargs)

    def render(
        self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs,
    ):
        if extra_context is None:
            extra_context = {}
        extra_context["adderURL"] = self.adderURL
        extra_context["adderTitle"] = self.adderTitle
        return super(AdderLayout, self).render(
            form, form_style, context, template_pack, extra_context, **kwargs
        )


class CustomURLField(forms.URLField):
    default_validators = [validators.CustomURLValidator()]
