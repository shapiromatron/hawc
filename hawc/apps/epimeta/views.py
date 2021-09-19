from django.db.models import Q

from ..common.views import (
    BaseCreate,
    BaseCreateWithFormset,
    BaseDelete,
    BaseDetail,
    BaseEndpointFilterList,
    BaseUpdate,
    BaseUpdateWithFormset,
    CopyAsNewSelectorMixin,
    WebappConfig,
)
from ..mgmt.views import EnsureExtractionStartedMixin
from ..study.models import Study
from . import forms, models


def get_app_config_metaprotocol(view, context) -> WebappConfig:
    return WebappConfig(
        app="epiMetaStartup", page="startupMetaProtocolPage", data=dict(id=view.object.id)
    )


def get_app_config_metaresult(view, context) -> WebappConfig:
    return WebappConfig(
        app="epiMetaStartup", page="startupMetaResultPage", data=dict(id=view.object.id)
    )


# MetaProtocol
class MetaProtocolCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = "Meta-protocol created."
    parent_model = Study
    parent_template_name = "study"
    model = models.MetaProtocol
    form_class = forms.MetaProtocolForm


class MetaProtocolDetail(BaseDetail):
    model = models.MetaProtocol
    get_app_config = get_app_config_metaprotocol


class MetaProtocolUpdate(BaseUpdate):
    success_message = "Meta-protocol updated."
    model = models.MetaProtocol
    form_class = forms.MetaProtocolForm


class MetaProtocolDelete(BaseDelete):
    success_message = "Meta-protocol deleted."
    model = models.MetaProtocol
    get_app_config = get_app_config_metaprotocol

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


class MetaResultCopyAsNew(CopyAsNewSelectorMixin, MetaProtocolDetail):
    copy_model = models.MetaResult
    form_class = forms.MetaResultSelectorForm


class MetaResultDetail(BaseDetail):
    model = models.MetaResult
    get_app_config = get_app_config_metaresult


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
    get_app_config = get_app_config_metaresult

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
