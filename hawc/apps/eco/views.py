from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import ListView

from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import BaseCreate, BaseDelete, BaseDetail, BaseUpdate
from ..study.models import Study
from . import filterset, forms, models


# Design
class DesignCreate(BaseCreate):
    success_message = "Study design created."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm

    def get_success_url(self):
        return self.object.get_update_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def get_design_relations(design):
    cause_effect = models.Study.objects.filter(id=design.study_id).prefetch_related(
        "eco_causes", "eco_effects"
    )
    results = models.Result.objects.filter(design=design.id)
    return {
        "causes": cause_effect[0].eco_causes.all(),
        "effects": cause_effect[0].eco_effects.all(),
        "results": results,
    }


class DesignUpdate(BaseUpdate):
    success_message = "Study design updated."
    parent_model = Study
    parent_template_name = "study"
    model = models.Design
    form_class = forms.DesignForm
    template_name = "eco/design_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_design_relations(self.object))
        return context


class DesignDetail(BaseDetail):
    model = models.Design
    template_name = "eco/design_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_design_relations(self.object))
        return context


class DesignDelete(BaseDelete):
    success_message = "Study Population deleted."
    model = models.Design

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_design_relations(self.object))
        return context

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Term preview
class NestedTermList(ListView):
    model = models.NestedTerm
    paginate_by = 2000
    filterset_class = filterset.NestedTermFilterset

    def include_ancestors(self, queryset=None):
        paths = queryset.values_list("path", "depth")
        parent_paths = set(queryset.values_list("path", flat=True))
        steplen = queryset.model.steplen
        for node in paths:  # for every node in the list,
            for parent_node in range(
                node[1]
            ):  # and for every parent of that node, (i.e. for the depth of the node)
                parent_paths.add(
                    node[0][0 : ((parent_node + 1) * steplen)]
                )  # grab the parent's path
        return queryset.model.objects.filter(path__in=parent_paths)

    def get_queryset(self):
        qs = self.filterset.qs
        if qs.count() == self.model.objects.all().count():
            return qs
        else:
            return self.include_ancestors(qs)

    def get_base_queryset(self):
        return models.NestedTerm.objects.all()

    def get_filterset_kwargs(self):
        return dict(
            data=self.request.GET,
            queryset=self.get_base_queryset(),
            request=self.request,
            assessment=None,
        )

    @property
    def filterset(self):
        if not hasattr(self, "_filterset"):
            self._filterset = self.filterset_class(**self.get_filterset_kwargs())
        return self._filterset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(form=self.filterset.form)
        return context


# Viewsets
class DesignViewset(HtmxViewSet):
    actions = {"read", "update"}
    parent_model = Study
    model = models.Design
    form_fragment = "eco/fragments/_design_edit.html"
    detail_fragment = "eco/fragments/_design_table.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = forms.DesignForm(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)


class DesignChildViewset(HtmxViewSet):
    actions = {"create", "read", "update", "delete", "clone"}
    parent_model = models.Design
    model = None  # required
    form_class = None  # required
    form_fragment = "eco/fragments/_object_edit_row.html"
    detail_fragment = None  # required

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        if request.method == "POST":
            form = self.form_class(request.POST, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = self.form_class(parent=request.item.parent)
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def update(self, request: HttpRequest, *args, **kwargs):
        template = self.form_fragment
        data = request.POST if request.method == "POST" else None
        form = self.form_class(data=data, instance=request.item.object)
        if request.method == "POST" and form.is_valid():
            self.perform_update(request.item, form)
            template = self.detail_fragment
        context = self.get_context_data(form=form)
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            context = {"attribute": self.model.__name__.lower(), "id": request.item.object.id}
            self.perform_delete(request.item)
            return render(request, "eco/fragments/_delete_rows.html", context)
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("post",), permission=can_edit)
    def clone(self, request: HttpRequest, *args, **kwargs):
        self.perform_clone(request.item)
        return render(request, self.detail_fragment, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model.__name__.lower()
        return context


class CauseViewset(DesignChildViewset):
    model = models.Cause
    form_class = forms.CauseForm
    detail_fragment = "eco/fragments/cause_row.html"


class EffectViewset(DesignChildViewset):
    model = models.Effect
    form_class = forms.EffectForm
    detail_fragment = "eco/fragments/effect_row.html"


class ResultViewset(DesignChildViewset):
    model = models.Result
    form_class = forms.ResultForm
    parent_model = models.Design
    detail_fragment = "eco/fragments/result_row.html"
