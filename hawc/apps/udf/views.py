import itertools

from django.core.exceptions import BadRequest, PermissionDenied
from django.http import HttpRequest
from django.shortcuts import render
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

from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from . import forms, models
from .cache import UDFCache


# UDF views
class UDFListView(LoginRequiredMixin, ListView):
    template_name = "udf/udf_list.html"
    model = models.UserDefinedForm

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .get_available_udfs(self.request.user)
            .prefetch_related("editors", "assessments")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for udf in context["object_list"]:
            udf.form = dynamic_forms.Schema.model_validate(udf.schema).to_form(prefix=udf.id)
            udf.can_edit = udf.user_can_edit(self.request.user)
        return context


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
        context = super().get_context_data(**kwargs)
        context["tag_object_list"] = list(
            models.TagBinding.objects.filter(assessment=self.assessment).prefetch_related(
                "tag", "form"
            )
        )
        for binding in itertools.chain(context["object_list"], context["tag_object_list"]):
            binding.form.can_edit = binding.form.user_can_edit(self.request.user)
        return context


class BindingViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete"}
    parent_model = Assessment
    model = models.ModelBinding
    form = forms.ModelBindingForm
    binding_type = "tag"

    form_fragment = "udf/fragments/binding_edit_row.html"
    detail_fragment = "udf/fragments/_udf_item.html"
    list_fragment = "udf/fragments/binding_list.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.binding_type = self.kwargs.get("binding_type", None)
        if self.binding_type == "tag":
            self.model = models.TagBinding
            self.form = forms.TagBindingForm
        elif self.binding_type == "model":
            self.model = models.ModelBinding
            self.form = forms.ModelBindingForm
        else:
            raise BadRequest("Must provide a 'tag' or 'model' binding_type argument.")
        return super().dispatch(request, *args, **kwargs)

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        # prefetch_related_objects([request.item.object], "admission_tags", "removal_tags")
        return render(
            request,
            self.detail_fragment,
            self.get_context_data(
                binding_type=self.binding_type,
                udf=request.item.object.form,
                binding=request.item.object,
            ),
        )

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = self.form(request.POST, parent=request.item.parent, user=request.user)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = self.form(parent=request.item.parent, user=request.user)
            template = self.list_fragment
        context = self.get_context_data(form=form)
        object_list = self.model.objects.filter(
            assessment=request.item.assessment
        ).prefetch_related("admission_tags", "removal_tags")
        context.update(
            object_list=object_list,
            binding_type=self.binding_type,
            udf=request.item.object.form,
            binding=request.item.object,
        )
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = self.form(request.POST, instance=request.item.object, user=request.user)
            if form.is_valid():
                self.perform_update(request.item, form)
                template = self.detail_fragment
        else:
            form = self.form(data=None, instance=request.item.object, user=request.user)
        context = self.get_context_data(
            form=form,
            binding_type=self.binding_type,
            udf=request.item.object.form,
            binding=request.item.object,
        )
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            self.perform_delete(request.item)
            return self.str_response()
        form = self.form(data=None, instance=request.item.object, user=request.user)
        context = self.get_context_data(form=form, binding_type=self.binding_type)
        return render(request, self.form_fragment, context)


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user)
        return kwargs

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
