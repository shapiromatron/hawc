from typing import Any, List, Tuple, Union

from crispy_forms import bootstrap as cfb
from crispy_forms import helper as cf
from crispy_forms import layout as cfl
from crispy_forms.utils import TEMPLATE_PACK, flatatt
from django import forms
from django.template.loader import render_to_string

from . import selectable, validators, widgets

ASSESSMENT_UNIQUE_MESSAGE = "Must be unique for assessment (current value already exists)."


def form_actions_create_or_close():
    """Add form actions to create or close the window (for popups)"""
    return [
        cfl.Submit("save", "Create"),
        cfl.HTML("""<a class="btn btn-light" href='#' onclick='window.close()'>Cancel</a>"""),
    ]


def form_actions_apply_filters():
    """Add form_actions to apply filters"""
    return [
        cfl.Submit("submit", "Apply filters"),
        cfl.HTML('<a class="btn btn-light" href=".">Reset</a>'),
    ]


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

        if "help_text" in self.kwargs:
            layout.insert(
                0,
                cfl.HTML(f'<p class="form-text text-muted">{self.kwargs["help_text"]}</p>'),
            )

        if "legend_text" in self.kwargs:
            layout.insert(0, cfl.HTML(f"<legend>{self.kwargs['legend_text']}</legend>"))

        form_actions = self.kwargs.get("form_actions")

        cancel_url = self.kwargs.get("cancel_url")
        if form_actions is None and cancel_url:
            form_actions = [
                cfl.Submit("save", self.kwargs.get("submit_text", "Save")),
                cfl.HTML(f'<a role="button" class="btn btn-light" href="{cancel_url}">Cancel</a>'),
            ]

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
            self[first + i].wrap(cfl.Column, css_class=class_)
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
        fld = selectable.AutoCompleteSelectField(
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
                lis.append(f"<li>{key}: {value}</li>")
    return lis


def form_error_lis_to_ul(lis):
    return f"<ul>{''.join(lis)}</ul>"


def addPopupLink(href, text):
    return f'<a href="{href}" onclick="return window.app.HAWCUtils.newWindowPopupLink(this);")>{text}</a>'


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
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs,
    ):
        if extra_context is None:
            extra_context = {}
        extra_context.update(adder_url=self.adder_url, adder_title=self.adder_title)
        return super().render(form, form_style, context, template_pack, extra_context, **kwargs)


class CustomURLField(forms.URLField):
    default_validators = [validators.CustomURLValidator()]


class ArrayCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """For use in ArrayField with a CharField with choices"""

    def format_value(self, value) -> List[str]:
        """Return selected values as a list."""
        if value is None:
            return []
        return value.split(",")


class QuillField(forms.CharField):
    """
    Quill text editor input.
    Cleans HTML and validates urls.
    """

    widget = widgets.QuillWidget

    def __init__(self, *args, **kwargs):
        # Force use of Quill widget
        kwargs["widget"] = self.widget
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        return validators.clean_html(value) if value else value

    def validate(self, value):
        super().validate(value)
        if value:
            validators.validate_hyperlinks(value)
