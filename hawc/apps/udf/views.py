from django.core.exceptions import BadRequest, PermissionDenied
from django.db.models import TextChoices
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView, UpdateView

from hawc.apps.assessment.models import Assessment
from hawc.apps.common import dynamic_forms
from hawc.apps.common.views import (
    BaseList,
    LoginRequiredMixin,
    MessageMixin,
    htmx_required,
)
from hawc.apps.lit.models import ReferenceFilterTag

from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from . import constants, forms, models
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


class BindingType(TextChoices):
    TAG = "tag"
    MODEL = "model"


class UDFBindingList(BaseList):
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.ModelBinding
    template_name = "udf/udfbinding_list.html"

    def get_queryset(self):
        return super().get_queryset().filter(assessment=self.assessment).order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            tag_binding=BindingType.TAG.value,
            model_binding=BindingType.MODEL.value,
            tag_object_list=list(
                models.TagBinding.objects.filter(assessment=self.assessment)
                .prefetch_related("tag", "form")
                .order_by("-created")
            ),
        )
        tag_names = ReferenceFilterTag.get_nested_tag_names(self.assessment.id)
        for binding in context["object_list"]:
            binding.form.can_edit = binding.form.user_can_edit(self.request.user)
        for binding in context["tag_object_list"]:
            binding.tag_name = tag_names[binding.tag.id]
            binding.form.can_edit = binding.form.user_can_edit(self.request.user)
        return context


class BindingViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete"}
    parent_model = Assessment
    model = models.ModelBinding
    form = forms.ModelBindingForm
    binding_type = BindingType = None

    form_fragment = "udf/fragments/binding_edit_row.html"
    detail_fragment = "udf/fragments/_udf_item.html"
    list_fragment = "udf/fragments/binding_list.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.binding_type = self.kwargs.get("binding_type", None)
        if self.binding_type == BindingType.TAG:
            self.model = models.TagBinding
            self.form = forms.TagBindingForm
        elif self.binding_type == BindingType.MODEL:
            self.model = models.ModelBinding
            self.form = forms.ModelBindingForm
        else:
            raise BadRequest("Must provide a 'tag' or 'model' binding_type argument.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            *args,
            **kwargs,
            tag_binding=BindingType.TAG.value,
            model_binding=BindingType.MODEL.value,
            binding_type=self.binding_type,
        )

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        udf = request.item.object.form
        udf.can_edit = udf.user_can_edit(self.request.user)
        if self.binding_type == BindingType.TAG:
            tag_names = ReferenceFilterTag.get_nested_tag_names(request.item.assessment.id)
            request.item.object.tag_name = tag_names[request.item.object.tag.id]
        return render(
            request,
            self.detail_fragment,
            self.get_context_data(
                udf=udf,
                binding=request.item.object,
            ),
        )

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = self.form(request.POST, parent=request.item.parent, user=request.user)
            context = self.get_context_data(form=form, binding_type=self.binding_type)
            if form.is_valid():
                self.perform_create(request.item, form)
                udf = request.item.object.form
                udf.can_edit = udf.user_can_edit(self.request.user)
                template = self.detail_fragment
                if self.binding_type == BindingType.TAG:
                    tag_names = ReferenceFilterTag.get_nested_tag_names(request.item.parent.id)
                    request.item.object.tag_name = tag_names[request.item.object.tag.id]
                context.update(udf=udf, binding=request.item.object)
        else:
            form = self.form(parent=request.item.parent, user=request.user)
            template = self.list_fragment
            object_list = models.ModelBinding.objects.filter(
                assessment=request.item.assessment
            ).order_by("-created")
            tag_object_list = models.TagBinding.objects.filter(
                assessment=request.item.assessment
            ).order_by("-created")
            context = self.get_context_data(
                form=form, object_list=object_list, tag_object_list=tag_object_list
            )
            tag_names = ReferenceFilterTag.get_nested_tag_names(request.item.parent.id)
            for binding in object_list:
                binding.form.can_edit = binding.form.user_can_edit(request.user)
            for binding in tag_object_list:
                if self.binding_type == BindingType.TAG:
                    binding.tag_name = tag_names[binding.tag.id]
                binding.form.can_edit = binding.form.user_can_edit(request.user)
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
        context = self.get_context_data(form=form)
        return render(request, self.form_fragment, context)


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
