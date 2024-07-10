from typing import Any

from crispy_forms import bootstrap as cfb
from crispy_forms import helper as cf
from crispy_forms import layout as cfl
from django import forms
from django.forms.widgets import RadioSelect
from django.urls import reverse

from . import validators, widgets
from .clean import sanitize_html
from .helper import PydanticToDjangoError

ASSESSMENT_UNIQUE_MESSAGE = "Must be unique for assessment (current value already exists)."


def check_unique_for_assessment(form: forms.ModelForm, field: str) -> Any:
    """Validate that item is unique for an assessment, and return the value.

    The `unique_together` restraints are normally checked in a ModelForm if both fields are
    available on that form; however, we generally dont expose the assessment ID as an input
    on the ModelForm for many models. This method can be used instead in the form clean methods.

    Args:
        form (forms.ModelForm): the bound form
        field (str): the field to check

    Raises:
        forms.ValidationError: If value is not unique for an assessment

    Returns:
        Any: The cleaned value
    """

    Model = form.instance.__class__
    value = form.cleaned_data[field]
    filters = {"assessment_id": form.instance.assessment.id, field: value}
    qs = Model.objects.filter(**filters)
    if form.instance.id:
        qs = qs.exclude(id=form.instance.id)
    if qs.exists():
        raise forms.ValidationError(ASSESSMENT_UNIQUE_MESSAGE)
    return value


def form_actions_create_or_close():
    """Add form actions to create or close the window (for popups)"""
    return [
        cfl.Submit("save", "Create"),
        cfl.HTML("""<a class="btn btn-light" href='#' onclick='window.close()'>Cancel</a>"""),
    ]


def form_actions_big(save_text="Save", cancel_url=".", cancel_text="Cancel"):
    """Create big, centered Submit and Cancel buttons for filter forms."""
    return cfl.HTML(
        f"""
        <div class="d-flex justify-content-center mb-4">
            <input type="submit" name="save" value="{save_text}" class="btn btn-primary mx-2 py-2" id="submit-id-save" style="width: 15rem; padding: 0.7rem;">
            <a role="button" class="btn btn-light mx-2 py-2" href="{cancel_url}" style="width: 8rem; padding: 0.7rem;">{cancel_text}</a>
        </div>
        """
    )


class BaseFormHelper(cf.FormHelper):
    include_media = False

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

    def get_layout_item(self, field_name: str) -> tuple[Any, int]:
        mapping = {pointer.name: pointer.positions for pointer in self.layout.get_field_names()}
        layout = self.layout
        for idx in mapping[field_name]:
            if layout[idx] == field_name:
                return (layout, idx)
            layout = layout[idx]
        raise ValueError("Cannot find item")  # pragma: no cover

    def add_create_btn(self, field_name: str, url: str, title: str):
        """
        Render field plus an "add new" button to the right.
        """
        layout, index = self.get_layout_item(field_name)
        field = layout[index]
        layout[index] = CreateNewButton(field, adder_url=url, adder_title=title)

    def add_row(self, firstField: str, numFields: int, classes: str | list[str]):
        if isinstance(classes, str):
            classes = [classes] * numFields
        first = self.layout.index(firstField)
        for i, class_ in enumerate(classes):
            self[first + i].wrap(cfl.Column, css_class=class_)
        self[first : first + numFields].wrap_together(
            cfl.Row, id=f"row_id_{firstField}_{numFields}"
        )

    def find_layout_idx_for_field_name(self, field_name: str) -> int:
        # Return the root layout index for a given field
        for idx, el in enumerate(self.layout):
            if isinstance(el, cfl.LayoutObject):
                for pointer in el.get_field_names():
                    if pointer.name == field_name:
                        return idx
            elif isinstance(el, str):
                if el == field_name:
                    return idx
        raise ValueError(f"Field not found: {field_name}")  # pragma: no cover

    def add_refresh_page_note(self):
        note = cfl.HTML(
            "<div class='alert alert-info'><b>Note:</b> If coming from an extraction form, you may need to refresh the extraction form to use the item which was recently created.</div>"
        )
        self.layout.insert(len(self.layout) - 1, note)

    def add_field_wraps(self):
        """Wrap django fields with crispy field wrappers.
        This should be performed after wrapping fields in rows and
        columns, since it can add additional wraps around a django
        field that can beyond the row/column containers.
        """
        for field_name, field in self.form.fields.items():
            if hasattr(field, "crispy_field_class"):
                self[field_name].wrap(field.crispy_field_class)


class CopyForm(forms.Form):
    legend_text: str
    help_text: str
    create_url_pattern: str
    selector: forms.ModelChoiceField

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent")
        super().__init__(*args, **kwargs)

    def get_success_url(self) -> str:
        item = self.cleaned_data["selector"]
        url = reverse(self.create_url_pattern, args=(self.parent.id,))
        return f"{url}?initial={item.id}"

    def get_cancel_url(self) -> str:
        return self.parent.get_absolute_url()

    @property
    def helper(self):
        return BaseFormHelper(
            self,
            legend_text=self.legend_text,
            help_text=self.help_text,
            cancel_url=self.get_cancel_url(),
            submit_text="Copy selected",
        )


class InlineFilterFormHelper(BaseFormHelper):
    """Helper class for creating an inline filtering form with a primary field."""

    def __init__(
        self,
        form,
        main_field: str,
        appended_fields: list[str],
        legend_text: str | None = None,
        help_text: str | None = None,
        **kwargs,
    ):
        """Inline form field helper, with primary search and appended fields.

        This form will have a single search bar with a primary search, inline
        appended fields, and inline cancel/search buttons.

        Args:
            form: form
            main_field: A text input field
            appended_fields: 1 or more checkbox or select fields (to right of main)
            legend_text: Legend text to show on the form
            help_text: help text to show on the form
            **kwargs: Extra arguments
        """
        self.attrs = {}
        self.kwargs = kwargs
        self.inputs = []
        self.form = form
        self.main_field = main_field
        self.appended_fields = appended_fields
        self.legend_text = legend_text
        self.help_text = help_text
        self.build_inline_layout()

    def build_inline_layout(self):
        """Build the custom inline layout, including the grid layout."""
        if self.main_field:
            self.layout = cfl.Layout(*list(self.form.fields.keys()))
            self.add_filter_field(self.main_field, self.appended_fields)
            if self.form.grid_layout:
                self.form.grid_layout.apply_layout(self)
        else:
            self.build_default_layout(self.form)
        return self.layout

    def add_filter_field(
        self,
        main_field: str,
        appended_fields: list[str],
        expandable: bool = False,
    ):
        """Add the primary filter field (noncollapsed field(s)) to start of layout."""
        layout, index = self.get_layout_item(main_field)
        field = layout.pop(index)
        for app_field in appended_fields:
            layout, index = self.get_layout_item(app_field)
            layout.pop(index)
        layout.insert(
            0,
            FilterFormField(
                fields=field,
                appended_fields=appended_fields,
                expandable=expandable,
            ),
        )


class ExpandableFilterFormHelper(InlineFilterFormHelper):
    """Helper class for an inline filtering form with collapsible advanced fields."""

    collapse_field_name: str = "is_expanded"

    def __init__(self, *args, **kwargs):
        """Collapsable form field helper, primary search and advanced.

        This form will have a single search bar with a primary search, and the
        ability to expand the bar for additional "advanced" search fields.

        Args:
            args: Arguments passed to InlineFilterFormHelper
            kwargs: Keyword arguments passed to InlineFilterFormHelper
        """
        super().__init__(*args, **kwargs)
        self.build_collapsed_layout()

    def build_collapsed_layout(self):
        """Build the custom collapsed layout including the grid layout."""
        if self.collapse_field_name not in self.form.fields:
            raise ValueError(f"Field `{self.collapse_field_name}` is required for this form")
        self.layout = cfl.Layout(*list(self.form.fields.keys()))
        layout, collapsed_idx = self.get_layout_item(self.collapse_field_name)
        collapsed_field = layout.pop(collapsed_idx)
        self.add_filter_field(self.main_field, self.appended_fields, expandable=True)
        self.layout.append(form_actions_big(save_text="Apply Filters"))
        form_index = 1
        if self.legend_text:
            self.layout.insert(0, cfl.HTML(f"<legend>{self.legend_text}</legend>"))
            form_index += 1
        if self.help_text:
            self.layout.insert(
                1,
                cfl.HTML(f'<p class="form-text text-muted">{self.help_text}</p>'),
            )
            form_index += 1
        if self.form.grid_layout:
            self.form.grid_layout.apply_layout(self)
        self[form_index:].wrap_together(cfl.Div, css_class="p-4")
        is_expanded = self.form.data.get(self.collapse_field_name, "false") == "true"
        self[form_index:].wrap_together(
            cfl.Div,
            id="ff-expand-form",
            css_class="collapse show" if is_expanded else "collapse",
        )
        self.layout.append(collapsed_field)
        return self.layout


class FilterFormField(cfl.Field):
    """Custom crispy form field that includes appended_fields in the context."""

    template = "common/crispy_layout_filter_field.html"

    def __init__(self, fields, appended_fields: list[str], expandable: bool = False, **kw):
        self.fields = fields
        self.appended_fields = appended_fields
        self.expandable = expandable
        super().__init__(fields, **kw)

    def render(self, form, context, extra_context=None, **kw):
        if extra_context is None:
            extra_context = {}
        extra_context.update(
            appended_fields=[form[field] for field in self.appended_fields],
            expandable=self.expandable,
        )
        return super().render(form, context, extra_context=extra_context, **kw)


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


class CreateNewButton(cfl.Field):
    """
    Adder layout object. It contains a link-button to add a new field.
    """

    template = "bootstrap4/field_create_new_button.html"

    def __init__(self, *args, **kwargs):
        self.adder_url = kwargs.pop("adder_url")
        self.adder_title = kwargs.pop("adder_title")
        super().__init__(*args, **kwargs)

    def render(self, form, context, extra_context=None, **kw):
        if extra_context is None:
            extra_context = {}
        extra_context.update(adder_url=self.adder_url, adder_title=self.adder_title)
        return super().render(form, context, extra_context=extra_context, **kw)


class CustomURLField(forms.URLField):
    default_validators = [validators.CustomURLValidator()]


class ArrayCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """For use in ArrayField with a CharField with choices"""

    def format_value(self, value) -> list[str]:
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
        return sanitize_html.clean_html(value) if value else value

    def validate(self, value):
        super().validate(value)
        if value:
            validators.validate_hyperlinks(value)


class ConfirmationField(forms.CharField):
    """A required field where a user must type in a fixed value; defaults to "confirm".

    Args:
        check_value (str): the value to check; defaults to "confirm".
    """

    def __init__(self, *args, **kw):
        self.check_value = kw.pop("check_value", "confirm")
        kwargs = dict(
            max_length=32, required=True, help_text=f'Please type "{self.check_value}" to proceed.'
        )
        kwargs.update(kw)
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        if value != self.check_value:
            raise forms.ValidationError(f'The value of "{self.check_value}" is required.')


class DynamicFormField(forms.JSONField):
    """Field to display dynamic form inline."""

    default_error_messages = {"invalid": "Invalid input"}
    widget = widgets.DynamicFormWidget

    def __init__(self, prefix, form_class, form_kwargs=None, *args, **kwargs):
        """Create dynamic form field."""
        self.form_class = form_class
        self.form_kwargs = {} if form_kwargs is None else form_kwargs
        self.widget = self.widget(prefix, form_class, form_kwargs)
        super().__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        """Get data to be shown for this field on render."""
        if self.disabled:
            return initial
        return data

    def validate(self, value):
        """Validate inline form."""
        super().validate(value)
        form = self.form_class(data=value, **self.form_kwargs)
        if not form.is_valid():
            raise forms.ValidationError(self.error_messages["invalid"])


class InlineRadioChoiceField(forms.ChoiceField):
    """Choice widget that uses radio buttons that are inline."""

    widget = RadioSelect
    crispy_field_class = cfb.InlineRadios


class PydanticValidator:
    """JSON field validator that uses a pydantic model."""

    def __init__(self, schema):
        """Set the schema."""
        self.schema = schema

    def __call__(self, value):
        """Validate the field with the pydantic model."""
        with PydanticToDjangoError(include_field=False):
            self.schema.model_validate(value)


# thx https://stackoverflow.com/questions/21754918/rendering-tabular-rows-with-formset-in-django-crispy-forms and https://stackoverflow.com/questions/42615357/cannot-pass-helper-to-django-crispy-formset-in-template
class FormsetGenericFormHelper(BaseFormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.template = "bootstrap4/table_inline_formset.html"
