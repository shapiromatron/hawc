import logging
import re
from typing import Literal

from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import ValidationError
from django.http import (
    HttpResponseBadRequest,
    HttpResponseRedirect,
    QueryDict,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView
from pydantic import BaseModel, Field, model_validator

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment
from ..assessment.views import check_published_status
from ..common.helper import PydanticToDjangoError
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseFilterList,
    BaseUpdate,
    Breadcrumb,
    htmx_required,
)
from ..lit.models import Reference
from ..mgmt.views import EnsurePreparationStartedMixin
from ..riskofbias.models import RiskOfBiasMetric
from ..udf.views import UDFDetailMixin
from . import filterset, forms, models

# from .actions.clone import clone_animal_bioassay, clone_epiv2, clone_rob, clone_study
from .actions.clone import clone_study

logger = logging.getLogger(__name__)


class StudyFilterList(BaseFilterList):
    template_name = "study/study_list.html"
    parent_model = Assessment
    model = models.Study
    filterset_class = filterset.StudyFilterSet
    paginate_by = 50

    def get_queryset(self):
        return super().get_queryset().distinct().prefetch_related("identifiers")

    def get_filterset_form_kwargs(self):
        if self.assessment.user_is_team_member_or_higher(self.request.user):
            return dict(
                main_field="query",
                appended_fields=["data_type", "published", "paginate_by"],
                dynamic_fields=["query", "data_type", "published", "paginate_by"],
            )
        else:
            return dict(
                main_field="query",
                appended_fields=["data_type", "paginate_by"],
                dynamic_fields=["query", "data_type", "paginate_by"],
            )


class StudyCreateFromReference(EnsurePreparationStartedMixin, BaseCreate):
    # Create Study from an existing lit.Reference.

    parent_model = Reference
    parent_template_name = "reference"
    model = models.Study
    form_class = forms.NewStudyFromReferenceForm
    success_message = "Study created."

    def dispatch(self, *args, **kwargs):
        # ensure if study already exists you can't create another
        study = self.model.objects.filter(pk=kwargs["pk"]).first()
        if study:
            return HttpResponseRedirect(study.get_update_url())
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        self.initial = dict(
            assessment=self.assessment,
            reference=self.parent,
            short_citation=self.parent.ref_short_citation,
            full_citation=self.parent.ref_full_citation,
        )
        return self.initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.assessment = self.assessment
        return form

    @transaction.atomic
    def form_valid(self, form):
        self.object = self.model.save_new_from_reference(self.parent, form.cleaned_data)
        self.create_log(self.object)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())


class ReferenceStudyCreate(EnsurePreparationStartedMixin, BaseCreate):
    """
    Creation of both a reference and study. Easier because there is no
    existing Reference instance in table, so we just create both at once.
    """

    success_message = "Study created."
    parent_model = Assessment
    parent_template_name = "assessment"
    model = models.Study
    form_class = forms.ReferenceStudyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manual_entry_warning"] = True
        return context

    def post_object_save(self, form):
        search = apps.get_model("lit", "Search").objects.get_manually_added(self.assessment)
        self.object.searches.add(search)


class IdentifierStudyCreate(ReferenceStudyCreate):
    """
    Create a study and optionally a reference, linked to an existing external database identifier.
    """

    form_class = forms.IdentifierStudyForm

    def get_success_url(self):
        return reverse_lazy("study:update", args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manual_entry_warning"] = False
        return context


@method_decorator(htmx_required, name="post")
class CloneStudies(BaseUpdate):
    # Show a list of eligible assessments to clone from.
    template_name = "study/study_clone.html"
    model = Assessment
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE
    form_class = forms.StudyCloneAssessmentSelectorForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(user=self.request.user, assessment=self.assessment)
        return kwargs

    def get_context_data(self, **kw):
        context = super().get_context_data()
        context["breadcrumbs"].insert(
            2, Breadcrumb(name="Studies", url=reverse("study:list", args=(self.assessment.id,)))
        )
        context["breadcrumbs"][-1].name = "Clone"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if not form.is_valid():
            return HttpResponseBadRequest("Bad assessment")

        form_action = request.POST.get("action")
        src_assessment = form.cleaned_data["src_assessment"]
        context = self.get_clone_context_data(src_assessment)
        match form_action:
            case "fetch":
                # check that assessment selected is a valid selection
                return render(request, "study/fragments/clone_fetch.html", context)
            case "clone":
                # check cloned data
                try:
                    studies_map = self.clone(context, request.POST.copy())
                except ValidationError as err:
                    logger.info(err)
                    return HttpResponseBadRequest("Bad clone request")
                return render(
                    request,
                    "study/fragments/clone_success.html",
                    {"now": timezone.now(), "studies_map": studies_map},
                )
            case _:
                return HttpResponseBadRequest("Bad request")

    def get_clone_context_data(self, src_assessment: Assessment):
        study_qs = models.Study.objects.filter(assessment=src_assessment)
        if not src_assessment.user_is_team_member_or_higher(self.request.user):
            study_qs = study_qs.published_only(True)
        src_metrics = (
            RiskOfBiasMetric.objects.assessment_qs(src_assessment)
            .select_related("domain")
            .order_by("domain__sort_order", "sort_order")
        )
        dst_metrics = (
            RiskOfBiasMetric.objects.assessment_qs(self.object)
            .select_related("domain")
            .order_by("domain__sort_order", "sort_order")
        )
        return {
            "assessment": self.object,
            "src_assessment": src_assessment,
            "studies": study_qs.deep_clone_annotations(),
            "src_metrics": src_metrics,
            "dst_metrics": dst_metrics,
        }

    def clone(self, context: dict, data: QueryDict):
        metric_map = {}
        for key, value in data.items():
            if value.isnumeric():
                if src_key := re.search(r"^metric-(\d+)$", key):
                    metric_map[src_key[0]] = value
        data["metric_map"] = metric_map

        # convert lists to into single items in QueryDict as needed
        with PydanticToDjangoError():
            model = CloneStudyDataValidation.model_validate(
                {
                    "study": data.getlist("study"),
                    "study_bioassay": data.getlist("study_bioassay"),
                    "study_epi": data.getlist("study_epi"),
                    "study_rob": data.getlist("study_rob"),
                    "include_rob": data.get("include_rob", False),
                    "copy_mode": data.get("copy_mode"),
                    "metric_map": data.get("metric_map", {}),
                }
            )

        diff = set(model.metric_map.keys()) - set(
            context["dst_metrics"].values_list("id", flat=True)
        )
        if diff:
            raise forms.ValidationError(f"Destination key(s) not found: {diff}")

        diff = set(model.metric_map.values()) - set(
            context["src_metrics"].values_list("id", flat=True)
        )
        if diff:
            raise forms.ValidationError(f"Source key(s) not found: {diff}")

        studies_map = model.clone(context)
        return studies_map


class CloneStudyDataValidation(BaseModel):
    study: set[int] = Field(min_length=1)
    study_bioassay: set[int]
    study_epi: set[int]
    study_rob: set[int]
    include_rob: bool = False
    copy_mode: Literal["final-to-initial", "final-to-final"] | None
    metric_map: dict[int, int]

    @model_validator(mode="after")
    def validate_after(self):
        if self.include_rob is False and len(self.study_rob) > 0:
            raise ValueError("Cannot include RoB without a study selected for RoB")
        elif self.include_rob and (len(self.metric_map) == 0):
            raise ValueError("Cannot include RoB without a RoB mapping")
        elif self.include_rob and (self.copy_mode is None):
            raise ValueError("Cannot include RoB without a copy mode specified")
        return self

    @transaction.atomic
    def clone(self, context: dict):
        studies = context["studies"].filter(id__in=self.study)
        # if self.metric_map:
        #     src_metrics = {el.id: el for el in context["src_metrics"]}
        #     dst_metrics = {el.id: el for el in context["dst_metrics"]}
        #     mapping = {
        #         src_metrics[key]: dst_metrics[value] for key, value in self.metric_map.items()
        #     }

        # src_assessment = context["src_assessment"]
        dst_assessment = context["assessment"]
        studies_map = {}
        for study in studies:
            src_study, dst_study = clone_study(study, dst_assessment)
            studies_map[src_study] = dst_study
            # clones["studies"].append({src_id: dst_id})
            # if src_id in self.study_bioassay:
            #     clone_animal_bioassay(src_id, dst_id)
            # if src_id in self.study_epi:
            #     clone_epiv2(src_id, dst_id)
            # if src_id in self.study_rob:
            #     clone_rob(src_study_id, dst_study_id, metric_map, clone_map)
            # TODO - add assessment.Log
            # TODO - return something for view showing mapping
        return studies_map


class StudyDetail(UDFDetailMixin, BaseDetail):
    model = models.Study

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        check_published_status(self.request.user, self.object.published, self.assessment)
        attachments_viewable = self.assessment.user_is_reviewer_or_higher(self.request.user)
        context["config"] = {
            "studyContent": self.object.get_json(json_encode=False),
            "attachments_viewable": attachments_viewable,
            "attachments": self.object.get_attachments_dict() if attachments_viewable else None,
        }
        context["internal_communications"] = self.object.get_communications()
        return context


class StudyToggleLock(RedirectView):
    pattern_name = "study:detail"

    def get(self, request, *args, **kwargs):
        study = get_object_or_404(models.Study, pk=kwargs["pk"])
        if not study.user_can_toggle_editable(self.request.user):
            raise PermissionDenied()
        study.toggle_editable()
        return super().get(request, *args, **kwargs)


class StudyUpdate(BaseUpdate):
    model = models.Study
    form_class = forms.StudyForm
    success_message = "Study updated."


class StudyDelete(BaseDelete):
    model = models.Study
    success_message = "Study deleted."

    def get_success_url(self):
        return reverse_lazy("study:list", kwargs={"pk": self.assessment.pk})


class StudyRoBRedirect(StudyDetail):
    # permanent redirect of RoB results; link is required to work based on
    # older OHAT reports which use this legacy URL route.

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return redirect(self.object.get_final_rob_url(), permanent=True)


# Attachment views
class AttachmentCreate(BaseCreate):
    success_message = "Attachment added to study."
    parent_model = models.Study
    parent_template_name = "study"
    model = models.Attachment
    form_class = forms.AttachmentForm

    def get_success_url(self):
        return reverse_lazy("study:detail", kwargs={"pk": self.parent.pk})


class AttachmentDelete(BaseDelete):
    success_message = "Attachment deleted."
    model = models.Attachment

    def get_success_url(self):
        self.parent = self.object.study
        return self.object.study.get_absolute_url()

    def get_cancel_url(self) -> str:
        return self.object.study.get_absolute_url()


class AttachmentDetail(BaseDetail):
    model = models.Attachment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.assessment.user_is_reviewer_or_higher(self.request.user):
            return HttpResponseRedirect(self.object.attachment.url)
        else:
            raise PermissionDenied
