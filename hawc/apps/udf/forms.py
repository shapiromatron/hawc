from copy import deepcopy
from crispy_forms import layout as cfl
from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.urls import reverse, reverse_lazy

from ..assessment.models import Assessment
from ..common.autocomplete.forms import AutocompleteSelectMultipleWidget
from ..common.dynamic_forms.schemas import Schema
from ..common.forms import BaseFormHelper, PydanticValidator, form_actions_big, DynamicFormField
from ..common.helper import get_current_user
from ..common.views import create_object_log
from ..lit.models import ReferenceFilterTag
from ..myuser.autocomplete import UserAutocomplete
from . import cache, constants, models

class FormAsField(forms.Field):
    # render a form as a field, something like a fieldset
    ### probably use DynamicFormField
    pass

class ArrayWidgetOld(forms.Widget):
    template_name = "udf/widget.html"

    class Media:
        js = (f"{settings.STATIC_URL}js/array.js",)

class ArrayFieldOld(forms.Field):
    # on render have the underlying field disabled & hidden. this will be copy & pasted on "create" click
    # add [] suffix to fields here so that they're POSTed as arrays (AlpineJS ideally, likely jQuery)
    # create & delete element buttons
    # arrow buttons for reordering
    widget = ArrayWidgetOld

    def __init__(self,field):
        self.field = field
        super().__init__()

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if isinstance(widget, ArrayWidgetOld) and "field" not in widget.attrs:
            attrs.setdefault("field", self.field)
        return attrs

class SchemaFieldForm(forms.Form):
    # use dynamic form w/ conditional? since we want different forms
    # depending on what field type is chosen
    # conditional logic may clash with js from array field (ie suffixes added to names)
    # may have to bring over HERO AlpineJS implementation of conditional logic to make it work
    pass

class ArrayWidget(forms.MultiWidget):
    # TODO: override template to create hidden input,
    # "Add" button that grabs hidden input and appends it,
    # "Delete" button that removes field
    # Ideally add & delete with alpineJS, if not then jQuery most likely

    template_name = "udf/widget.html"

    #class Media:
        # may not be necessary if done entirely with alpineJS
        #js = (f"{settings.STATIC_URL}js/array.js",)

    def __init__(self, default_widget, attrs=None):
        super(forms.MultiWidget,self).__init__(attrs)
        self.default_widget = default_widget
        self.suffix = "[]"
        self.widgets_names = []
        self.widgets = []

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # TODO handle this more like in super?
        context["default_widget"] = self.default_widget.get_context(name+self.suffix, None, attrs)["widget"]
        return context

    def initialize_widgets(self, widgets:list):
        self.widgets_names = [self.suffix for _ in range(len(widgets))]
        self.widgets = [w() if isinstance(w, type) else w for w in widgets]

    def initialize_widgets_from_fields(self, fields:list):
        widgets = [field.widget for field in fields]
        self.initialize_widgets(widgets)

    def value_from_datadict(self, data, files, name):
        #import pdb; pdb.set_trace()
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get

        # TODO replace this logic with index based logic;
        # should look cleaner here, but trickier on frontend
        keys = [_ for _ in data.keys() if _.startswith(name+self.suffix)]
        lists = [getter(key) for key in keys]
        values = [{(name + k.removeprefix(name+self.suffix)):v[i] for i,k in enumerate(keys)} for v in zip(*lists)]

        
        if values:
            foo = [
                self.default_widget.value_from_datadict(value, files, name)
                for value in values
            ]
            #import pdb; pdb.set_trace()
            return foo
        
        return getter(name) or []

    def value_omitted_from_data(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        values = {index:value for index, value in enumerate(getter(name+self.suffix) or [])}
        return all(
            widget.value_omitted_from_data(values, files, index)
            for index, widget in enumerate(self.widgets)
        )
    
    def decompress(self, value):
        # no need to decompress; value should always be a list
        return value


class ArrayField(forms.MultiValueField):
    widget = ArrayWidget

    def __init__(self, field, *, require_all_fields=True, **kwargs):
        widget = kwargs.get("widget") or self.widget
        if isinstance(widget, type):
            kwargs["widget"] = widget(default_widget=field.widget)
        super(forms.MultiValueField,self).__init__(**kwargs)
        self.require_all_fields = require_all_fields
        self.field = field
        self.fields = []

    def initialize_fields(self, fields:list):
        for f in fields:
            f.error_messages.setdefault("incomplete", self.error_messages["incomplete"])
            if self.disabled:
                f.disabled = True
            if self.require_all_fields:
                # Set 'required' to False on the individual fields, because the
                # required validation will be handled by MultiValueField, not
                # by those individual fields.
                f.required = False
        self.fields = fields

        self.widget.initialize_widgets_from_fields(self.fields)

    def initialize_fields_from_value(self, value:list):
        #import pdb; pdb.set_trace()
        fields = [deepcopy(self.field) for _ in value]
        self.initialize_fields(fields)

    def compress(self, data_list):
        # no compression; we want the array
        # ie check clean method, it returns this
        return data_list


class FieldForm(forms.Form):
    type = forms.ChoiceField(
        required=True,
        choices=(
            ("boolean", "Boolean"),
            ("char", "Text"),
            ("integer", "Integer"),
            ("float", "Float"),
            ("choice", "Choice"),
            ("yes_no", "Yes/No"),
            ("multiple_choice", "Multiple Choice"),
        ),
    )
    name = forms.CharField(required=True)
    required = forms.BooleanField(required=False)
    label = forms.CharField(required=False)
    label_suffix = forms.CharField(required=False)
    # initial = anything (ie same as condition comparison_value)
    help_text = forms.CharField(required=False)
    css_class = forms.CharField(required=False)

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Column("type"),
            ),
            cfl.Row(
                cfl.Column("name"),
                cfl.Column("required"),
            ),
            cfl.Row(
                cfl.Column("label"),
                cfl.Column("label_suffix"),
                cfl.Column("help_text"),
            ),
            cfl.Row(
                cfl.Column("css_class"),
            ),
        )
        return helper

class ConditionForm(forms.Form):
    subject = forms.CharField(required=False)
    observers = forms.CharField(required=False) # make array, test
    # comparison = select field
    # comparison_value = anything (not sure how to do this, maybe conditional logic)
    # behavior = select field

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        return helper


class Foobar(forms.Form):
    fields = ArrayField(DynamicFormField(prefix="schema_builder-fields",form_class=FieldForm))
    #conditions = ArrayField(DynamicFormField(required=False,prefix="schema_builder-conditions",form_class=ConditionForm))

    def __init__(self,*args,**kwargs):
        #kwargs.pop("instance")
        #kwargs.pop("user")
        #kwargs["data"] = {"fields":[1,2,3]}
        super().__init__(*args,**kwargs)
        #import pdb; pdb.set_trace()
        #self.fields["fields"].initialize_fields_from_value(kwargs.get("data",{}).get("fields",[]))
        #self.fields["conditions"].initialize_fields_from_value(kwargs.get("data",{}).get("conditions",[]))
        #import pdb; pdb.set_trace()
        self.fields["fields"].initialize_fields_from_value(self.fields["fields"].widget.value_from_datadict(self.data, None, 'schema_builder-fields') or [])
        #self.fields["conditions"].initialize_fields_from_value(self.fields["conditions"].widget.value_from_datadict(self.data, None, "conditions") or [])
        #import pdb; pdb.set_trace()
        return
    

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        return helper

class UDFForm(forms.ModelForm):
    schema_builder = DynamicFormField(
        prefix="schema_builder",
        form_class=Foobar,
        validators=[PydanticValidator(Schema)],)


    schema = forms.JSONField(
        initial=Schema(fields=[]).model_dump(),
        validators=[PydanticValidator(Schema)],
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if schema:=self.initial.get("schema"):
            self.initial["schema_builder"] = schema
        if self.instance.id is None:
            self.instance.creator = user

        # filter assessment list to a subset of those available
        self.fields["assessments"].queryset = (
            Assessment.objects.all().user_can_view(self.instance.creator).order_by("name")
        )
        self.fields[
            "assessments"
        ].help_text += (
            f" Only assessments the creator ({self.instance.creator}) can view are shown."
        )

        self.fields["schema"].label_append_button = {
            "btn_attrs": {
                "hx-indicator": "#spinner",
                "id": "schema-preview-btn",
                "hx-post": reverse_lazy("udf:schema_preview"),
                "hx-target": "#schema-preview-fieldset",
                "hx-swap": "innerHTML",
                "class": "ml-2 btn btn-primary",
            },
            "btn_content": "Preview",
        }
        self.fields["schema"].help_text = (
            models.UserDefinedForm.schema.field.help_text
            + "&nbsp;<a id='load-example' href='#'>Load an example</a>."
        )

    def clean_name(self):
        # check unique_together ("creator", "name")
        name = self.cleaned_data.get("name")
        if (
            name != self.instance.name
            and self._meta.model.objects.filter(creator=self.instance.creator, name=name).exists()
        ):
            raise forms.ValidationError("The UDF name must be unique for your account.")
        return name

    def clean(self):
        #import pdb; pdb.set_trace()
        # remove errors if schema has manually been changed
        cleaned_data = super().clean()
        if "schema" in self.changed_data:
            self._errors.pop("schema_builder",None)
        elif "schema_builder" in cleaned_data:
            cleaned_data["schema"] = cleaned_data["schema_builder"]
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        verb = "Created" if self.instance.id is None else "Updated"
        instance = super().save(commit=commit)
        if commit:
            create_object_log(verb, instance, None, self.instance.creator_id, "")
        return instance

    class Meta:
        model = models.UserDefinedForm
        fields = (
            "name",
            "description",
            "schema",
            "editors",
            "assessments",
            "published",
            "deprecated",
        )
        widgets = {
            "editors": AutocompleteSelectMultipleWidget(UserAutocomplete),
        }

    @property
    def helper(self):
        legend_text = (
            "Update User Defined Fields (UDF)"
            if self.instance.id
            else "Create a set of User Defined Fields (UDF)"
        )
        helper = BaseFormHelper(self)
        helper.set_textarea_height(("description",), 8)
        helper.layout = cfl.Layout(
            cfl.Fieldset(
                legend_text,
                cfl.Row(
                    cfl.Column("name", css_class="col-md-6"),
                    cfl.Column(
                        "published",
                        "deprecated" if self.instance.id else None,
                        css_class="col-md-6 align-items-center d-flex",
                    ),
                ),
                cfl.Row(
                    cfl.Column("description", css_class="col-md-6"),
                    cfl.Column("editors", "assessments", css_class="col-md-6"),
                ),
                css_class="fieldset-border mx-2 mb-4",
            ),
            cfl.Fieldset(
                "Form Schema",
                cfl.Row(
                    cfl.Column("schema_builder"),
                ),
                cfl.Row(
                    cfl.Column("schema"),
                ),
                cfl.Row(
                    cfl.Fieldset(
                        legend="",
                        css_id="schema-preview-fieldset",
                        css_class="bg-lightblue rounded w-100 box-shadow p-4 mx-3 mt-2 mb-4 collapse",
                    )
                ),
                css_class="fieldset-border mx-2 mb-4",
            ),
            form_actions_big(cancel_url=reverse("udf:udf_list")),
        )
        return helper







class UDFForm1(forms.ModelForm):
    schema = forms.JSONField(
        initial=Schema(fields=[]).model_dump(),
        validators=[PydanticValidator(Schema)],
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            self.instance.creator = user

        # filter assessment list to a subset of those available
        self.fields["assessments"].queryset = (
            Assessment.objects.all().user_can_view(self.instance.creator).order_by("name")
        )
        self.fields[
            "assessments"
        ].help_text += (
            f" Only assessments the creator ({self.instance.creator}) can view are shown."
        )

        self.fields["schema"].label_append_button = {
            "btn_attrs": {
                "hx-indicator": "#spinner",
                "id": "schema-preview-btn",
                "hx-post": reverse_lazy("udf:schema_preview"),
                "hx-target": "#schema-preview-fieldset",
                "hx-swap": "innerHTML",
                "class": "ml-2 btn btn-primary",
            },
            "btn_content": "Preview",
        }
        self.fields["schema"].help_text = (
            models.UserDefinedForm.schema.field.help_text
            + "&nbsp;<a id='load-example' href='#'>Load an example</a>."
        )

    def clean_name(self):
        # check unique_together ("creator", "name")
        name = self.cleaned_data.get("name")
        if (
            name != self.instance.name
            and self._meta.model.objects.filter(creator=self.instance.creator, name=name).exists()
        ):
            raise forms.ValidationError("The UDF name must be unique for your account.")
        return name

    @transaction.atomic
    def save(self, commit=True):
        verb = "Created" if self.instance.id is None else "Updated"
        instance = super().save(commit=commit)
        if commit:
            create_object_log(verb, instance, None, self.instance.creator_id, "")
        return instance

    class Meta:
        model = models.UserDefinedForm
        fields = (
            "name",
            "description",
            "schema",
            "editors",
            "assessments",
            "published",
            "deprecated",
        )
        widgets = {
            "editors": AutocompleteSelectMultipleWidget(UserAutocomplete),
        }

    @property
    def helper(self):
        legend_text = (
            "Update User Defined Fields (UDF)"
            if self.instance.id
            else "Create a set of User Defined Fields (UDF)"
        )
        helper = BaseFormHelper(self)
        helper.set_textarea_height(("description",), 8)
        helper.layout = cfl.Layout(
            cfl.Fieldset(
                legend_text,
                cfl.Row(
                    cfl.Column("name", css_class="col-md-6"),
                    cfl.Column(
                        "published",
                        "deprecated" if self.instance.id else None,
                        css_class="col-md-6 align-items-center d-flex",
                    ),
                ),
                cfl.Row(
                    cfl.Column("description", css_class="col-md-6"),
                    cfl.Column("editors", "assessments", css_class="col-md-6"),
                ),
                css_class="fieldset-border mx-2 mb-4",
            ),
            cfl.Fieldset(
                "Form Schema",
                cfl.Row(
                    cfl.Column("schema"),
                ),
                cfl.Row(
                    cfl.Fieldset(
                        legend="",
                        css_id="schema-preview-fieldset",
                        css_class="bg-lightblue rounded w-100 box-shadow p-4 mx-3 mt-2 mb-4 collapse",
                    )
                ),
                css_class="fieldset-border mx-2 mb-4",
            ),
            form_actions_big(cancel_url=reverse("udf:udf_list")),
        )
        return helper



class SchemaPreviewForm(forms.Form):
    """Form for previewing a Dynamic Form schema."""

    schema = forms.JSONField(validators=[PydanticValidator(Schema)])


class ModelBindingForm(forms.ModelForm):
    assessment = forms.ModelChoiceField(
        queryset=Assessment.objects.all(), disabled=True, widget=forms.HiddenInput
    )
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.annotate(
            full_name=Concat(F("app_label"), Value("."), F("model"))
        ).filter(full_name__in=constants.SUPPORTED_MODELS)
    )

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("parent", None)
        user = kwargs.pop("user", None)
        prefix = f"model-{kwargs.get("instance").pk if "instance" in kwargs else "new"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if self.instance.id is None:
            # include assessment for unique_together validation
            self.fields["assessment"].initial = self.assessment
            self.instance.assessment = self.assessment
            self.instance.creator = user
        self.fields["form"].queryset = models.UserDefinedForm.objects.all().get_available_udfs(
            user, self.assessment
        )

    class Meta:
        model = models.ModelBinding
        fields = ("assessment", "content_type", "form")

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Column("form"),
                cfl.Column(
                    cfl.HTML('<p style="font-size: 1.25rem;">bound to</p>'),
                    css_class="col-md-auto d-flex align-items-center px-4",
                ),
                cfl.Column("content_type"),
            )
        )
        return helper


class TagBindingForm(forms.ModelForm):
    assessment = forms.ModelChoiceField(
        queryset=Assessment.objects.all(), disabled=True, widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop("parent", None)
        user = kwargs.pop("user", None)
        prefix = f"tag-{kwargs.get("instance").pk if "instance" in kwargs else "new"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if self.instance.id is None:
            # include assessment for unique_together validation
            self.fields["assessment"].initial = self.assessment
            self.instance.assessment = self.assessment
            self.instance.creator = user
        qs = ReferenceFilterTag.get_assessment_qs(self.instance.assessment_id)
        self.fields["tag"].queryset = qs
        self.fields["tag"].choices = [(el.id, el.get_nested_name()) for el in qs]
        self.fields["form"].queryset = models.UserDefinedForm.objects.all().get_available_udfs(
            user, self.assessment
        )

    class Meta:
        model = models.TagBinding
        fields = ("assessment", "tag", "form")

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Column("form"),
                cfl.Column(
                    cfl.HTML('<p style="font-size: 1.25rem;">bound to</p>'),
                    css_class="col-md-auto d-flex align-items-center px-4",
                ),
                cfl.Column("tag"),
            )
        )
        return helper


class UDFModelFormMixin:
    """Add UDF to model form."""

    def set_udf_field(self, assessment: Assessment):
        """Set UDF field on model form in a binding exists."""

        self.model_binding = cache.UDFCache.get_model_binding(
            assessment=assessment, Model=self.Meta.model
        )
        if self.model_binding:
            udf_content = models.ModelUDFContent.get_instance(assessment, self.instance)
            initial = udf_content.content if udf_content else None
            udf = self.model_binding.form_field(label="User Defined Fields", initial=initial)
            self.fields["udf"] = udf

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit and "udf" in self.changed_data:
            obj, created = models.ModelUDFContent.objects.update_or_create(
                defaults=dict(content=self.cleaned_data["udf"]),
                model_binding=self.model_binding,
                content_type=self.model_binding.content_type,
                object_id=instance.id,
            )
            create_object_log(
                "",
                obj,
                self.model_binding.assessment_id,
                get_current_user().id,
                f"Updated UDF data for model type {self.model_binding.content_type} on instance {instance.id} (binding {self.model_binding.id}).",
            )
        return instance
