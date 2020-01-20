from django.db.models import Q

from ..assessment.models import Assessment
from ..mgmt.views import EnsureExtractionStartedMixin
from ..study.models import Study
from ..utils.views import (
    BaseCreate,
    BaseCreateWithFormset,
    BaseDelete,
    BaseDetail,
    BaseEndpointFilterList,
    BaseList,
    BaseUpdate,
    BaseUpdateWithFormset,
)
from . import exports, forms, models


# MetaProtocol
class MetaProtocolCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Meta-protocol created."
    parent_model = Study
    parent_template_name = "study"
    model = models.MetaProtocol
    form_class = forms.MetaProtocolForm


class MetaProtocolDetail(BaseDetail):
    model = models.MetaProtocol


class MetaProtocolUpdate(BaseUpdate):
    success_message = "Meta-protocol updated."
    model = models.MetaProtocol
    form_class = forms.MetaProtocolForm


class MetaProtocolDelete(BaseDelete):
    success_message = "Meta-protocol deleted."
    model = models.MetaProtocol

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# MetaResult
class MetaResultCreate(BaseCreateWithFormset):
    success_message = "Meta-Result created."
    parent_model = models.MetaProtocol
    parent_template_name = "protocol"
    model = models.MetaResult
    form_class = forms.MetaResultForm
    formset_factory = forms.SingleResultFormset

    def post_object_save(self, form, formset):
        # Bind newly created single-result outcome to meta-result instance
        for form in formset.forms:
            form.instance.meta_result = self.object

    def get_formset_kwargs(self):
        return {"assessment": self.assessment}

    def build_initial_formset_factory(self):
        return forms.SingleResultFormset(
            queryset=models.SingleResult.objects.none(), **self.get_formset_kwargs()
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["assessment"] = self.assessment
        return kwargs


class MetaResultCopyAsNew(MetaProtocolDetail):
    template_name = "epimeta/metaresult_copy_selector.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = forms.MetaResultSelectorForm(study_id=self.object.study_id)
        return context


class MetaResultDetail(BaseDetail):
    model = models.MetaResult


class MetaResultUpdate(BaseUpdateWithFormset):
    success_message = "Meta-Result updated."
    model = models.MetaResult
    form_class = forms.MetaResultForm
    formset_factory = forms.SingleResultFormset

    def get_formset_kwargs(self):
        return {"assessment": self.assessment}

    def build_initial_formset_factory(self):
        return forms.SingleResultFormset(
            queryset=self.object.single_results.all().order_by("pk"), **self.get_formset_kwargs()
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["assessment"] = self.assessment
        return kwargs

    def post_object_save(self, form, formset):
        # Bind single-result outcome to meta-result instance, if adding new
        for form in formset.forms:
            form.instance.meta_result = self.object


class MetaResultDelete(BaseDelete):
    success_message = "Meta-Result deleted."
    model = models.MetaResult

    def get_success_url(self):
        return self.object.protocol.get_absolute_url()


class MetaResultList(BaseEndpointFilterList):
    model = models.MetaResult
    form_class = forms.MetaResultFilterForm

    def get_query(self, perms):
        query = Q(protocol__study__assessment=self.assessment)

        if not perms["edit"]:
            query &= Q(protocol__study__published=True)
        return query


class MetaResultFullExport(BaseList):
    parent_model = Assessment
    model = models.MetaResult

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        exporter = exports.MetaResultFlatComplete(
            self.object_list,
            export_format="excel",
            filename=f"{self.assessment}-epi-meta-analysis",
            sheet_name="epi-meta-analysis",
        )
        return exporter.build_response()
