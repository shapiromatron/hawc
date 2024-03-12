from typing import Self

import reversion
from crispy_forms.utils import render_crispy_form
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import JSONField
from django.urls import reverse
from django.utils.safestring import SafeText

from ..assessment.models import Assessment
from ..common import dynamic_forms
from ..common.forms import DynamicFormField


class UserDefinedForm(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    schema = models.JSONField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="udf_forms_creator"
    )
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="udf_forms")
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    deprecated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("creator", "name"),)
        ordering = ("-last_updated",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("udf:udf_detail", args=(self.pk,))

    def user_can_edit(self, user):
        return self.creator == user or user in self.editors.all()


class ModelBinding(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="udf_bindings"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    form = models.ForeignKey(UserDefinedForm, on_delete=models.CASCADE, related_name="models")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="udf_models"
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        indexes = (models.Index(fields=["assessment", "content_type"]),)
        unique_together = (("assessment", "content_type"),)

    def __str__(self):
        return f"{self.assessment} / {self.content_type.model} form"

    def form_field(self, *args, **kwargs) -> JSONField | DynamicFormField:
        prefix = kwargs.pop("prefix", "udf")
        form_kwargs = kwargs.pop("form_kwargs", None)
        return dynamic_forms.Schema.model_validate(self.form.schema).to_form_field(
            prefix, form_kwargs, *args, **kwargs
        )

    def form_instance(self, *args, **kwargs) -> dynamic_forms.DynamicForm:
        return dynamic_forms.Schema.model_validate(self.form.schema).to_form(*args, **kwargs)

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse("udf:model_detail", args=(self.id,))

    @classmethod
    def get_binding(cls, assessment: Assessment, Model: type[models.Model]) -> Self | None:
        content_type = ContentType.objects.get_for_model(Model)
        return assessment.udf_bindings.filter(content_type=content_type).first()


class TagBinding(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="udf_tag_bindings"
    )
    tag = models.ForeignKey(
        "lit.ReferenceFilterTag", on_delete=models.CASCADE, related_name="udf_forms"
    )
    form = models.ForeignKey(UserDefinedForm, on_delete=models.CASCADE, related_name="tags")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="udf_tags"
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        indexes = (models.Index(fields=["assessment", "tag"]),)
        unique_together = (("assessment", "tag"),)

    def __str__(self):
        return f"{self.form} form bound to {self.tag} tag"

    def form_field(
        self, prefix="", form_kwargs=None, *args, **kwargs
    ) -> JSONField | DynamicFormField:
        return dynamic_forms.Schema.model_validate(self.form.schema).to_form_field(
            prefix, form_kwargs, *args, **kwargs
        )

    def form_instance(self, *args, **kwargs) -> dynamic_forms.DynamicForm:
        return dynamic_forms.Schema.model_validate(self.form.schema).to_form(*args, **kwargs)

    def get_form_html(self, **kwargs) -> SafeText:
        form = dynamic_forms.Schema.model_validate(self.form.schema).to_form(
            prefix=self.tag_id, **kwargs
        )
        return render_crispy_form(form, helper=form.helper)

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse("udf:tag_detail", args=(self.id,))


class ModelUDFContent(models.Model):
    model_binding = models.ForeignKey(
        ModelBinding, on_delete=models.CASCADE, related_name="saved_contents"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    content = models.JSONField(blank=True, default=dict)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("model_binding", "content_type", "object_id"),)

    def get_content_as_list(self):
        schema = dynamic_forms.Schema.model_validate(self.model_binding.form.schema)
        items = []
        for field in schema.fields:
            field_value = self.content.get(field.name)
            field_kwargs = field.get_form_field_kwargs()
            value = field_value
            if "choices" in field_kwargs and field_value is not None:
                choice_map = dict(field_kwargs["choices"])
                value = (
                    "|".join([choice_map[i] for i in field_value])
                    if isinstance(value, list)
                    else choice_map[field_value]
                )
            if value:
                label = field.get_verbose_name()
                items.append((label, value))
        return items

    @classmethod
    def get_instance(cls, assessment_id, object: models.Model) -> Self | None:
        if object.pk is None:
            return
        return (
            cls.objects.filter(
                model_binding__assessment=assessment_id,
                content_type=ContentType.objects.get_for_model(object),
                object_id=object.pk,
            )
            .select_related("model_binding")
            .first()
        )


class TagUDFContent(models.Model):
    reference = models.ForeignKey(
        "lit.Reference", on_delete=models.CASCADE, related_name="saved_tag_contents"
    )
    tag_binding = models.ForeignKey(TagBinding, on_delete=models.PROTECT)
    content = models.JSONField(blank=True, default=dict)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("reference", "tag_binding"),)

    def get_content_as_list(self):
        # todo - refactor
        schema = dynamic_forms.Schema.model_validate(self.tag_binding.form.schema)

        items = []
        for field in schema.fields:
            field_value = self.content.get(field.name)
            field_kwargs = field.get_form_field_kwargs()
            if "choices" in field_kwargs and field_value is not None:
                choice_map = dict(field_kwargs["choices"])
                if field.type == "multiple_choice":
                    value = [choice_map[i] for i in field_value]
                else:
                    value = choice_map[field_value]
            else:
                value = field_value
            if value:
                label = field.get_verbose_name()
                if isinstance(value, list) and field.type != "multiple_choice":
                    value = "|".join(map(str, value))
                items.append((label, value))
        return items


reversion.register(TagBinding)
reversion.register(ModelBinding)
reversion.register(UserDefinedForm)
reversion.register(TagUDFContent)
