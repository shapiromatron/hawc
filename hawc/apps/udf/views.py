from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView, UpdateView

from hawc.apps.assessment.models import Assessment
from hawc.apps.common import dynamic_forms
from hawc.apps.common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseList,
    BaseUpdate,
    LoginRequiredMixin,
    MessageMixin,
    htmx_required,
)

from . import forms, models
from .cache import UDFCache


# UDF views
class UDFListView(LoginRequiredMixin, ListView):
    template_name = "udf/udf_list.html"
    model = models.UserDefinedForm


class UDFDetailView(LoginRequiredMixin, DetailView):
    template_name = "udf/udf_detail.html"
    model = models.UserDefinedForm

    def get_context_data(self, **kwargs):
        form = dynamic_forms.Schema.model_validate(self.object.schema).to_form()
        kwargs.update(form=form)
        return super().get_context_data(**kwargs)

    def user_can_edit(self):
        return self.object.user_can_edit(self.request.user)


class CreateUDFView(LoginRequiredMixin, MessageMixin, CreateView):
    template_name = "udf/udf_form.html"
    form_class = forms.UDFForm
    success_url = reverse_lazy("udf:udf_list")
    success_message = "Form created."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs


class UpdateUDFView(MessageMixin, UpdateView):
    template_name = "udf/udf_form.html"
    form_class = forms.UDFForm
    model = models.UserDefinedForm
    success_url = reverse_lazy("udf:udf_list")
    success_message = "Form updated."

    def get_object(self, **kw):
        obj = super().get_object(**kw)
        if not obj.user_can_edit(self.request.user):
            raise PermissionDenied()
        return obj

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs


@method_decorator(htmx_required, name="dispatch")
class SchemaPreview(LoginRequiredMixin, FormView):
    """Custom form schema preview view. Utilizes HTMX."""

    template_name = "udf/schema_preview.html"

    form_class = forms.SchemaPreviewForm
    http_method_names = ["post"]
    field_name = "schema"

    def get_form_kwargs(self):
        """Get form keyword arguments (the schema)."""
        return {"data": {"schema": self.request.POST.get(self.field_name)}}

    def get_context_data(self, **kwargs):
        """Get context data used in the template. Add field and modal ID."""
        kwargs.update(field=self.field_name, modal_id=f"{self.field_name}-preview")
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """Process a valid dynamic form/schema."""
        dynamic_form = dynamic_forms.Schema.model_validate(form.cleaned_data["schema"]).to_form(
            prefix=self.field_name
        )
        return self.render_to_response(self.get_context_data(valid=True, form=dynamic_form))

    def form_invalid(self, form):
        """Process invalid dynamic form/schema."""
        return self.render_to_response(self.get_context_data(valid=False))


class UDFBindingList(BaseList):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.ModelBinding

    def get_queryset(self):
        return super().get_queryset().filter(assessment=self.assessment)

    def get_context_data(self, **kwargs):
        kwargs.update(tag_object_list=models.TagBinding.objects.filter(assessment=self.assessment))
        return super().get_context_data(**kwargs)


# Model binding views
class CreateModelBindingView(BaseCreate):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.ModelBinding
    form_class = forms.ModelBindingForm
    success_message = "Model form binding created."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_success_url(self):
        return self.assessment.get_udf_list_url()


class ModelBindingDetailView(BaseDetail):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.ModelBinding


class UpdateModelBindingView(BaseUpdate):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.ModelBinding
    form_class = forms.ModelBindingForm
    success_message = "Model form binding updated."

    def get_success_url(self):
        return self.assessment.get_udf_list_url()


class DeleteModelBindingView(BaseDelete):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.ModelBinding
    success_message = "Model form binding deleted."

    def get_success_url(self):
        return self.assessment.get_udf_list_url()


# Tag binding views
class CreateTagBindingView(BaseCreate):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.TagBinding
    form_class = forms.TagBindingForm
    success_message = "Tag form binding created."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

    def get_success_url(self):
        return self.assessment.get_udf_list_url()


class TagBindingDetailView(BaseDetail):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.TagBinding


class UpdateTagBindingView(BaseUpdate):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.TagBinding
    form_class = forms.TagBindingForm
    success_message = "Tag form binding updated."

    def get_success_url(self):
        return self.assessment.get_udf_list_url()


class DeleteTagBindingView(BaseDelete):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.TagBinding
    success_message = "Tag form binding deleted."

    def get_success_url(self):
        return self.assessment.get_udf_list_url()


class UDFDetailMixin:
    """Mixin to add saved UDF contents to the context of a BaseDetail view."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_binding = UDFCache.get_model_binding_cache(self.assessment, self.model)
        context["udf_content"] = (
            UDFCache.get_udf_contents_cache(model_binding, self.object.pk)
            if model_binding is not None
            else None
        )
        return context
