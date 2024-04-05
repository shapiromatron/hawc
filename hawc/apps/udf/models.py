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
from . import managers


class UserDefinedForm(models.Model):
    objects = managers.UserDefinedFormManager()

    name = models.CharField(max_length=128)
    description = models.TextField()
    schema = models.JSONField(
        help_text="The schema defines the structure and behavior of the UDF. It is composed of JSON that specifies fields and conditional logic. Contact us for help defining a schema for your UDF."
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="udf_forms_creator"
    )
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="udf_forms",
        help_text="Editors have the ability to update this form, and can use it for any of their assessments.",
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    assessments = models.ManyToManyField(
        Assessment,
        blank=True,
        related_name="udf_forms",
        help_text="Users in selected assessments will be able to apply this form to models in their assessment.",
    )
    published = models.BooleanField(
        default=False,
        help_text="Published UDFs are visible for all users and usable for all assessments.",
    )
    deprecated = models.BooleanField(
        default=False, help_text="Select if this UDF should no longer be used."
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("creator", "name"),)
        ordering = ("-last_updated",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("udf:udf_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("udf:udf_update", args=(self.pk,))

    def user_can_edit(self, user):
        return self.creator == user or user in self.editors.all() or user.is_staff

    def data_list(self, data: dict):
        schema = dynamic_forms.Schema.model_validate(self.schema)
        return schema.to_list(data)


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

    def get_update_url(self):
        return reverse("udf:binding_update", args=("model", self.id))

    def get_delete_url(self):
        return reverse("udf:binding_delete", args=("model", self.id))

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

    def get_update_url(self):
        return reverse("udf:binding_update", args=("tag", self.id))

    def get_delete_url(self):
        return reverse("udf:binding_delete", args=("tag", self.id))


class ModelUDFContent(models.Model):
    model_binding = models.ForeignKey(
        ModelBinding, on_delete=models.CASCADE, related_name="saved_contents"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    content = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("model_binding", "content_type", "object_id"),)

    def get_content_as_list(self):
        return self.model_binding.form.data_list(self.content)

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
            .select_related("model_binding__form")
            .first()
        )


class TagUDFContent(models.Model):
    reference = models.ForeignKey(
        "lit.Reference", on_delete=models.CASCADE, related_name="saved_tag_contents"
    )
    tag_binding = models.ForeignKey(TagBinding, on_delete=models.CASCADE)
    content = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("reference", "tag_binding"),)

    def get_content_as_list(self):
        return self.tag_binding.form.data_list(self.content)


reversion.register(UserDefinedForm)
reversion.register(ModelBinding)
reversion.register(TagBinding)
reversion.register(ModelUDFContent)
reversion.register(TagUDFContent)
