from django.conf import settings
from django.core.exceptions import BadRequest, PermissionDenied
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView, UpdateView

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..common import dynamic_forms
from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import BaseList, LoginRequiredMixin, MessageMixin, htmx_required
from ..lit.models import ReferenceFilterTag
from . import constants, forms, models


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

    def get_form_class(self):
        """Return the form class to use in this view."""
        return forms.NewUDFForm if settings.HAWC_FEATURES.ENABLE_SCHEMA_BUILDER else forms.UDFForm

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

    def get_form_class(self):
        """Return the form class to use in this view."""
        return forms.NewUDFForm if settings.HAWC_FEATURES.ENABLE_SCHEMA_BUILDER else forms.UDFForm

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
    template_name = "udf/udfbinding_list.html"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER

    def get_queryset(self):
        return super().get_queryset().filter(assessment=self.assessment).order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            tag_binding=constants.BindingType.TAG.value,
            model_binding=constants.BindingType.MODEL.value,
            tag_object_list=list(
                models.TagBinding.objects.filter(assessment=self.assessment)
                .prefetch_related("tag", "form")
                .order_by("-created")
            ),
        )
        tag_names = ReferenceFilterTag.get_nested_tag_names(self.assessment.id)
        for binding in context["tag_object_list"]:
            binding.tag_name = tag_names[binding.tag_id]
        return context


class BindingViewSet(HtmxViewSet):
    actions = {"create", "read", "update", "delete"}
    parent_model = Assessment
    model = models.ModelBinding
    form = forms.ModelBindingForm
    binding_type = BindingType = None

    form_fragment = "udf/fragments/binding_edit_row.html"
    detail_fragment = "udf/fragments/udf_row.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.binding_type = self.kwargs.get("binding_type", None)
        if self.binding_type == constants.BindingType.TAG:
            self.model = models.TagBinding
            self.form = forms.TagBindingForm
        elif self.binding_type == constants.BindingType.MODEL:
            self.model = models.ModelBinding
            self.form = forms.ModelBindingForm
        else:
            raise BadRequest("Must provide a 'tag' or 'model' binding_type argument.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            *args,
            **kwargs,
            tag_binding=constants.BindingType.TAG.value,
            model_binding=constants.BindingType.MODEL.value,
            binding_type=self.binding_type,
        )

    def add_tag_names(self, tag_binding, assessment_id):
        if self.binding_type == constants.BindingType.TAG:
            tag_names = ReferenceFilterTag.get_nested_tag_names(assessment_id)
            if isinstance(tag_binding, list) or isinstance(tag_binding, QuerySet):
                for binding in tag_binding:
                    binding.tag_name = tag_names[binding.tag.id]
            else:
                tag_binding.tag_name = tag_names[tag_binding.tag.id]

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        udf = request.item.object.form
        self.add_tag_names(request.item.object, request.item.assessment.id)
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
        form_data = request.POST if request.method == "POST" else None
        form = self.form(data=form_data, parent=request.item.parent, user=request.user)
        context = self.get_context_data(form=form)
        if request.method == "POST" and form.is_valid():
            self.perform_create(request.item, form)
            udf = request.item.object.form
            template = self.detail_fragment
            self.add_tag_names(request.item.object, request.item.assessment.id)
            context.update(udf=udf, binding=request.item.object)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        form_data = request.POST if request.method == "POST" else None
        form = self.form(data=form_data, instance=request.item.object, user=request.user)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
            self.add_tag_names(request.item.object, request.item.assessment.id)
        return render(
            request,
            template,
            self.get_context_data(
                form=form,
                udf=request.item.object.form,
                binding=request.item.object,
            ),
        )

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            self.perform_delete(request.item)
            return self.str_response()
        form = self.form(data=None, instance=request.item.object, user=request.user)
        context = self.get_context_data(form=form)
        return render(request, self.form_fragment, context)


class UDFDetailMixin:
    """Add UDF content to a BaseDetail."""

    def get_context_data(self, **kw):
        context = super().get_context_data(**kw)
        context.update(
            udf_content=models.ModelUDFContent.get_instance(self.assessment, self.object)
        )
        return context
