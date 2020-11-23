from typing import Any, List, Tuple, Union

import selectable.forms as selectable
from crispy_forms import bootstrap as cfb
from crispy_forms import helper as cf
from crispy_forms import layout as cfl
from crispy_forms.utils import TEMPLATE_PACK, flatatt
from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from selectable.forms.widgets import SelectableMediaMixin

from . import validators


def build_form_actions(cancel_url: str, save_text: str = "Save", cancel_text: str = "Cancel"):
    return [
        cfl.Submit("save", save_text),
        cfl.HTML(f'<a role="button" class="btn btn-light" href="{cancel_url}">{cancel_text}</a>'),
    ]


class SelectableBootstrapMediaMixin(SelectableMediaMixin):
    class Media:
        css = SelectableMediaMixin.Media.css
        js = (
            *SelectableMediaMixin.Media.js,
            str(settings.PROJECT_PATH / "static/js/selectable_bootstrap.js"),
        )


class AutoCompleteWidget(selectable.AutoCompleteWidget, SelectableBootstrapMediaMixin):
    pass


class AutoCompleteSelectWidget(selectable.AutoCompleteSelectWidget, SelectableBootstrapMediaMixin):
    primary_widget = AutoCompleteWidget


class AutoCompleteSelectMultipleWidget(
    selectable.AutoCompleteSelectMultipleWidget, SelectableBootstrapMediaMixin
):
    primary_widget = AutoCompleteWidget


class AutoCompleteSelectField(selectable.AutoCompleteSelectField):
    widget = AutoCompleteSelectWidget


class AutoCompleteSelectMultipleField(selectable.AutoCompleteSelectMultipleField):
    widget = AutoCompleteSelectMultipleWidget


class BaseFormHelper(cf.FormHelper):

    error_text_inline = False
    use_custom_control = True

    def __init__(self, form=None, **kwargs):
        self.attrs = {}
        self.inputs = []
        self.kwargs = kwargs

        if form:
            self.form = form
            self.layout = self.build_default_layout(form)

    def build_default_layout(self, form):
        layout = cfl.Layout(*list(form.fields.keys()))

        if "legend_text" in self.kwargs:
            layout.insert(0, cfl.HTML(f"<legend>{self.kwargs['legend_text']}</legend>"))

        if "help_text" in self.kwargs:
            layout.insert(
                1, cfl.HTML(f'<p class="form-text text-muted">{self.kwargs["help_text"]}</p>'),
            )

        form_actions = self.kwargs.get("form_actions")
        if "cancel_url" in self.kwargs:
            form_actions = build_form_actions(self.kwargs["cancel_url"])
        if form_actions:
            layout.append(cfb.FormActions(*form_actions, css_class="form-actions"))

        return layout

    def get_layout_item(self, field_name: str) -> Tuple[Any, int]:
        mapping = {field: index for index, field in self.layout.get_field_names()}
        layout = self.layout
        for idx in mapping[field_name]:
            if layout[idx] == field_name:
                return (layout, idx)
            layout = layout[idx]
        raise ValueError("Cannot find item")

    def add_create_btn(self, field_name: str, url: str, title: str):
        """
        Render field plus an "add new" button to the right.
        """
        layout, index = self.get_layout_item(field_name)
        field = layout[index]
        layout[index] = AdderLayout(field, adder_url=url, adder_title=title)

    def add_row(self, firstField: str, numFields: int, classes: Union[str, List[str]]):
        if isinstance(classes, str):
            classes = [classes] * numFields
        first = self.layout.index(firstField)
        for i, class_ in enumerate(classes):
            self[first + i].wrap(cfl.Column, wrapper_class=class_)
        self[first : first + numFields].wrap_together(
            cfl.Row, id=f"row_id_{firstField}_{numFields}"
        )

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

    def add_refresh_page_note(self):
        note = cfl.HTML(
            "<div class='alert alert-info'><b>Note:</b> If coming from an extraction form, you may need to refresh the extraction form to use the item which was recently created.</div>"
        )
        self.layout.insert(len(self.layout) - 1, note)


class CopyAsNewSelectorForm(forms.Form):
    label = None
    lookup_class = None

    def __init__(self, *args, **kwargs):
        parent_id = kwargs.pop("parent_id")
        super(CopyAsNewSelectorForm, self).__init__(*args, **kwargs)
        self.setupSelector(parent_id)

    @property
    def helper(self):
        return BaseFormHelper(self)

    def setupSelector(self, parent_id):
        fld = AutoCompleteSelectField(
            lookup_class=self.lookup_class,
            allow_new=False,
            label=self.label,
            widget=selectable.AutoComboboxSelectWidget,
        )
        fld.widget.update_query_parameters({"related": parent_id})
        fld.widget.attrs["class"] = "col-md-10"
        self.fields["selector"] = fld


def form_error_list_to_lis(form):
    # Convert a list of errors from a form into a list of li,
    # used for endpoint group since everything is controlled by AJAX and JSON
    lis = []
    for key, values in form.errors.items():
        for value in values:
            if key == "__all__":
                lis.append(f"<li>{value}</li>")
            else:
                lis.append("<li>{key}: {value}</li>")
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
        self.adder_url = kwargs.pop("adder_url")
        self.adder_title = kwargs.pop("adder_title")
        super().__init__(*args, **kwargs)

    def render(
        self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs,
    ):
        if extra_context is None:
            extra_context = {}
        extra_context.update(adder_url=self.adder_url, adder_title=self.adder_title)
        return super().render(form, form_style, context, template_pack, extra_context, **kwargs)


class CustomURLField(forms.URLField):
    default_validators = [validators.CustomURLValidator()]
