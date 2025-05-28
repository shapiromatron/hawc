from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, TemplateView

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..assessment.views import check_published_status
from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig, tryParseInt
from ..common.views import (
    BaseCopyForm,
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseUpdate,
    add_csrf,
)
from . import constants, filterset, forms, models, serializers


def get_visual_list_crumb(assessment) -> Breadcrumb:
    return Breadcrumb(
        name="Visualizations", url=reverse("summary:visualization_list", args=(assessment.id,))
    )


def get_table_list_crumb(assessment) -> Breadcrumb:
    return Breadcrumb(
        name="Summary tables", url=reverse("summary:tables_list", args=(assessment.id,))
    )


# SUMMARY TABLE
class GetSummaryTableMixin:
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        slug = self.kwargs.get("slug")
        assessment = self.kwargs.get("pk")
        obj = get_object_or_404(models.SummaryTable, assessment=assessment, slug=slug)
        obj = super().get_object(object=obj)
        check_published_status(self.request.user, obj.published, self.assessment)
        return obj


class SummaryTableList(BaseFilterList):
    parent_model = Assessment
    model = models.SummaryTable
    filterset_class = filterset.SummaryTableFilterSet
    breadcrumb_active_name = "Summary tables"

    def get_filterset_form_kwargs(self):
        if self.assessment.user_is_team_member_or_higher(self.request.user):
            return dict(
                main_field="title",
                appended_fields=["type", "label", "published"],
            )
        else:
            return dict(
                main_field="title",
                appended_fields=["type", "label"],
                dynamic_fields=["title", "type", "label"],
            )


class SummaryTableDetail(GetSummaryTableMixin, BaseDetail):
    model = models.SummaryTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context["object"].published is False and context["obj_perms"]["edit"] is False:
            raise PermissionDenied()
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_table_list_crumb(self.assessment)
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(app="summaryTableViewStartup", data=dict(table_id=self.object.id))


class SummaryTableCreateSelector(BaseCreate):
    success_message = None
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.SummaryTable
    form_class = forms.SummaryTableSelectorForm
    template_name = "summary/summarytable_selector.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_table_list_crumb(self.assessment)
        )
        return context

    def form_valid(self, form):
        url = reverse(
            "summary:tables_create",
            args=(
                form.assessment.id,
                form.cleaned_data["table_type"],
            ),
        )
        return HttpResponseRedirect(url)


class SummaryTableCreate(BaseCreate):
    success_message = "Summary table created."
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.SummaryTable
    form_class = forms.SummaryTableForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            table_type = constants.TableType(self.kwargs["table_type"])
        except ValueError as err:
            raise Http404() from err
        kwargs["table_type"] = table_type
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_table_list_crumb(self.assessment)
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="summaryTableEditStartup",
            data=dict(
                assessment_id=self.assessment.id,
                is_create=True,
                initial=serializers.SummaryTableSerializer(context["form"].instance).data,
                save_url=models.SummaryTable.get_api_list_url(self.assessment.id),
                cancel_url=models.SummaryTable.get_list_url(self.assessment.id),
                csrf=get_token(self.request),
            ),
        )


class SummaryTableCopy(BaseCopyForm):
    copy_model = models.SummaryTable
    form_class = forms.SummaryTableCopySelectorForm
    model = Assessment

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.update(parent=self.assessment, user=self.request.user)
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Copy existing",
            [Breadcrumb.from_object(self.assessment), get_table_list_crumb(self.assessment)],
        )
        return context


class SummaryTableUpdate(GetSummaryTableMixin, BaseUpdate):
    success_message = "Summary table updated."
    model = models.SummaryTable
    form_class = forms.SummaryTableForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_table_list_crumb(self.assessment)
        )
        return context

    def get_app_config(self, context) -> WebappConfig:
        return WebappConfig(
            app="summaryTableEditStartup",
            data=dict(
                assessment_id=self.assessment.id,
                is_create=False,
                initial=serializers.SummaryTableSerializer(self.object).data,
                save_url=self.object.get_api_url(),
                cancel_url=self.object.get_absolute_url(),
                csrf=get_token(self.request),
            ),
        )


class SummaryTableDelete(GetSummaryTableMixin, BaseDelete):
    success_message = "Summary table deleted."
    model = models.SummaryTable

    def get_success_url(self):
        return self.model.get_list_url(self.assessment.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_table_list_crumb(self.assessment)
        )
        return context


# VISUALIZATIONS
class GetVisualizationObjectMixin:
    def get_object(self):
        slug = self.kwargs.get("slug")
        assessment = self.kwargs.get("pk")
        obj = get_object_or_404(models.Visual, assessment=assessment, slug=slug)
        obj = super().get_object(object=obj)
        check_published_status(self.request.user, obj.published, self.assessment)
        return obj


class VisualizationList(BaseFilterList):
    parent_model = Assessment
    model = models.Visual
    breadcrumb_active_name = "Visualizations"
    filterset_class = filterset.VisualFilterSet

    def get_filterset_form_kwargs(self):
        if self.assessment.user_is_team_member_or_higher(self.request.user):
            return dict(
                main_field="title",
                appended_fields=["type", "label", "published"],
            )
        else:
            return dict(
                main_field="title",
                appended_fields=["type", "label"],
                dynamic_fields=["title", "type", "label"],
            )


class VisualizationByIdDetail(RedirectView):
    """
    Redirect to standard visual page; useful for developers referencing by database id.
    """

    def get_redirect_url(*args, **kwargs):
        return get_object_or_404(models.Visual, id=kwargs.get("pk")).get_absolute_url()


class LegacyDataPivotRedirect(RedirectView):
    def get_redirect_url(*args, **kwargs):
        obj = get_object_or_404(
            models.Visual, assessment=kwargs.get("pk"), dp_slug=kwargs.get("slug")
        )
        return obj.get_absolute_url()


class VisualizationDetail(GetVisualizationObjectMixin, BaseDetail):
    model = models.Visual

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        context.update(config=add_csrf(self.object.read_config(), self.request))
        return context

    def get_template_names(self):
        if self.object.visual_type in (
            constants.VisualType.DATA_PIVOT_QUERY,
            constants.VisualType.DATA_PIVOT_FILE,
        ):
            return ["summary/visual_detail_dp.html"]
        elif self.object.visual_type == constants.VisualType.PLOTLY:
            return ["summary/visual_detail_plotly.html"]
        elif self.object.visual_type == constants.VisualType.IMAGE:
            return ["summary/visual_detail_image.html"]
        elif self.object.visual_type == constants.VisualType.PRISMA:
            return ["summary/visual_detail_prisma.html"]
        else:
            return super().get_template_names()


class VisualizationCreateSelector(BaseDetail):
    model = Assessment
    template_name = "summary/visual_selector.html"
    breadcrumb_active_name = "Visualization selector"

    def get_context_data(self, **kwargs):
        kwargs.update(action="Create", url_copy="summary:visualization_create")
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context


def get_visual_form_config(form: forms.VisualForm, crud: str, csrf: str, cancel_url: str):
    config = dict(
        assessment=form.instance.assessment.id,
        crud=crud,
        isCreate=crud == "Create",
        visual_type=form.instance.visual_type,
        evidence_type=form.instance.evidence_type,
        data_url=reverse("summary:api:visual-list"),
        csrf=csrf,
        cancel_url=cancel_url,
    )
    form.update_form_config(config)
    return config


class VisualizationCreate(BaseCreate):
    success_message = "Visualization created."
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.Visual

    def get_form_class(self):
        try:
            self.visual_type = constants.VisualType(self.kwargs.get("visual_type"))
        except ValueError as err:
            raise Http404() from err

        return forms.get_visual_form(self.visual_type)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        evidence_type = tryParseInt(self.kwargs.get("study_type"))
        initial = self._get_initial(filters=dict(visual_type=self.visual_type))
        if initial:
            evidence_type = initial["evidence_type"]

        if evidence_type is None:
            evidence_type = constants.get_default_evidence_type(self.visual_type)
        else:
            try:
                evidence_type = constants.StudyType(evidence_type)
            except ValueError as err:
                raise Http404() from err

        if evidence_type not in constants.VISUAL_EVIDENCE_CHOICES[self.visual_type]:
            raise Http404()

        kwargs.update(visual_type=self.visual_type, evidence_type=evidence_type, initial=initial)
        return kwargs

    def get_template_names(self):
        visual_type = int(self.kwargs.get("visual_type"))
        if visual_type in constants.WIP_VISUALS and not settings.HAWC_FEATURES.ENABLE_WIP_VISUALS:
            raise PermissionDenied()
        if visual_type in {
            constants.VisualType.BIOASSAY_AGGREGATION,
            constants.VisualType.LITERATURE_TAGTREE,
            constants.VisualType.EXTERNAL_SITE,
            constants.VisualType.PLOTLY,
            constants.VisualType.IMAGE,
            constants.VisualType.DATA_PIVOT_QUERY,
            constants.VisualType.DATA_PIVOT_FILE,
        }:
            return ["summary/visual_form_django.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            smart_tag_form=forms.SmartTagForm(assessment_id=self.assessment.id),
            config=get_visual_form_config(
                form=context["form"],
                crud=context["crud"],
                csrf=get_token(self.request),
                cancel_url=reverse("summary:visualization_list", args=(self.assessment.id,)),
            ),
        )
        context["form"].update_context(context)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1,
            get_visual_list_crumb(self.assessment),
        )
        return context

    def get_success_url(self):
        if self.object.is_data_pivot:
            return self.object.get_dp_update_settings()
        return super().get_success_url()


class VisualizationCopySelector(BaseDetail):
    model = Assessment
    template_name = "summary/visual_selector.html"
    breadcrumb_active_name = "Visualization selector"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE

    def get_context_data(self, **kwargs):
        kwargs.update(action="Copy", url_copy="summary:visualization_copy")
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 1, get_visual_list_crumb(self.assessment)
        )
        return context


class VisualizationCopy(BaseCopyForm):
    copy_model = models.Visual
    form_class = forms.VisualSelectorForm
    model = Assessment

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.update(
            visual_type=self.kwargs["visual_type"],
            queryset=models.Visual.objects.clonable_queryset(self.request.user).filter(
                visual_type=self.kwargs["visual_type"]
            ),
        )
        return kw

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Copy existing",
            [Breadcrumb.from_object(self.assessment), get_visual_list_crumb(self.assessment)],
        )
        return context


class VisualizationUpdate(GetVisualizationObjectMixin, BaseUpdate):
    success_message = "Visualization updated."
    model = models.Visual

    def get_form_class(self):
        return forms.get_visual_form(self.object.visual_type)

    def get_template_names(self):
        visual_type = self.object.visual_type
        if visual_type in [] and not settings.HAWC_FEATURES.ENABLE_WIP_VISUALS:
            raise PermissionDenied()
        if visual_type in (
            constants.VisualType.DATA_PIVOT_QUERY,
            constants.VisualType.DATA_PIVOT_FILE,
        ):
            return ["summary/visual_form_dp.html"]
        elif visual_type in {
            constants.VisualType.BIOASSAY_AGGREGATION,
            constants.VisualType.LITERATURE_TAGTREE,
            constants.VisualType.EXTERNAL_SITE,
            constants.VisualType.PLOTLY,
            constants.VisualType.IMAGE,
            constants.VisualType.DATA_PIVOT_QUERY,
            constants.VisualType.DATA_PIVOT_FILE,
        }:
            return ["summary/visual_form_django.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            smart_tag_form=forms.SmartTagForm(assessment_id=self.assessment.id),
            config=get_visual_form_config(
                form=context["form"],
                crud=context["crud"],
                csrf=get_token(self.request),
                cancel_url=reverse("summary:visualization_list", args=(self.assessment.id,)),
            ),
        )
        context["form"].update_context(context)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        return context

    def get_success_url(self):
        if self.object.is_data_pivot:
            return self.object.get_dp_update_settings()
        return super().get_success_url()


class VisualizationUpdateSettings(GetVisualizationObjectMixin, BaseUpdate):
    success_message = "Visualization updated."
    model = models.Visual
    form_class = forms.VisualSettingsForm
    template_name = "summary/visual_update_settings.html"

    def get_object(self, **kw):
        object = super().get_object(**kw)
        if not object.is_data_pivot:
            raise Http404()
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        context["config"] = {
            "data_url": self.object.get_data_url() + "?format=tsv",
            "settings": self.object.settings,
        }
        return context


class VisualizationDelete(GetVisualizationObjectMixin, BaseDelete):
    success_message = "Visualization deleted."
    model = models.Visual

    def get_success_url(self):
        return reverse_lazy("summary:visualization_list", kwargs={"pk": self.assessment.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"].insert(
            len(context["breadcrumbs"]) - 2, get_visual_list_crumb(self.assessment)
        )
        return context


class DatasetInteractivity(TemplateView):
    template_name = "summary/dataset_interactivity.html"
