from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from hawc.apps.common.crumbs import Breadcrumb

from ..assessment.models import Assessment
from ..assessment.views import check_published_status
from ..common.views import BaseCreate, BaseDelete, BaseDetail, BaseFilterList, BaseUpdate
from ..lit.models import Reference
from ..mgmt.views import EnsurePreparationStartedMixin
from ..udf.views import UDFDetailMixin
from . import filterset, forms, models


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


class StudyClone(BaseUpdate):
    """
    Copy studies along with all study information from one assessment to another.
    """

    template_name = "study/study_clone.html"
    # parent_template_name = "assessment"
    # parent_model = Assessment
    model = Assessment
    form_class = forms.StudyCloneForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["study_data"] = {}
        assessments = Assessment.objects.all().user_can_view(
            self.request.user, exclusion_id=self.assessment.id
        )
        for dst_assessment in assessments:
            context["study_data"][f"studies_assessment_{dst_assessment.id}"] = (
                models.Study.objects.filter(assessment=dst_assessment)
            )
            for study in context["study_data"][f"studies_assessment_{dst_assessment.id}"]:
                study.rob = len(study.get_active_robs(with_final=False)) > 0

        context["breadcrumbs"] = Breadcrumb.build_assessment_crumbs(
            self.request.user, self.assessment
        )
        context["breadcrumbs"].append(Breadcrumb(name="Deep Clone"))
        return context

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.update(user=self.request.user, assessment=self.assessment)
        return kw


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
