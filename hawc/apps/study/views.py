from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView

from ..assessment.models import Assessment
from ..common.crumbs import Breadcrumb
from ..common.htmx import HtmxViewSet, action, can_edit, can_view
from ..common.views import (
    BaseCreate,
    BaseDelete,
    BaseDetail,
    BaseList,
    BaseUpdate,
    MessageMixin,
    TeamMemberOrHigherMixin,
)
from ..lit.models import Reference
from ..mgmt.views import EnsurePreparationStartedMixin
from . import forms, models


class StudyList(BaseList):
    parent_model = Assessment
    model = models.Study
    form_class = forms.StudyFilterForm

    def get_query(self, qs, perms):
        query = Q(assessment=self.assessment)
        if not perms["edit"]:
            query &= Q(published=True)
        return qs.filter(query)

    def get_queryset(self):
        perms = super().get_obj_perms()
        qs = super().get_queryset()
        qs = self.get_query(qs, perms)
        initial = self.request.GET if len(self.request.GET) > 0 else None  # bound vs unbound
        self.form = self.form_class(data=initial, can_edit=perms["edit"])
        if self.form.is_valid():
            qs = qs.filter(self.form.get_query())
        return qs.distinct().prefetch_related("identifiers")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study_list"] = self.get_queryset()
        context["form"] = self.form
        return context


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

    def post_object_save(self, form):
        search = apps.get_model("lit", "Search").objects.get_manually_added(self.assessment)
        self.object.searches.add(search)


class StudyRead(BaseDetail):
    model = models.Study

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attachments_viewable = self.assessment.user_is_part_of_team(self.request.user)
        context["config"] = {
            "studyContent": self.object.get_json(json_encode=False),
            "attachments_viewable": attachments_viewable,
        }
        context["attachments"] = (
            models.Attachment.objects.get_attachments(
                self.get_object(), not context["obj_perms"]["edit"]
            )
            if attachments_viewable
            else None
        )
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


class StudiesCopy(TeamMemberOrHigherMixin, MessageMixin, FormView):
    """
    Copy one or more studies from one assessment to another. This will copy
    all nested data as well.
    """

    model = Assessment
    template_name = "study/studies_copy.html"
    form_class = forms.StudiesCopy

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assessment"] = self.assessment
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Copy study",
            extras=[
                Breadcrumb.from_object(self.assessment),
                Breadcrumb(name="Studies", url=reverse("study:list", args=(self.assessment.id,))),
            ],
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["assessment"] = self.assessment
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        models.Study.copy_across_assessment(
            form.cleaned_data["studies"], form.cleaned_data["assessment"]
        )
        msg = "Studies copied!"
        self.success_message = msg
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("study:list", kwargs={"pk": self.assessment.id})


class StudyRoBRedirect(StudyRead):
    # permanent redirect of RoB results; link is required to work based on
    # older OHAT reports which use this legacy URL route.

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return redirect(self.object.get_final_rob_url(), permanent=True)


# Attachment viewset
class AttachmentViewset(HtmxViewSet):
    actions = {"create", "read", "delete"}
    parent_model = models.Study
    model = models.Attachment
    form_fragment = "study/attachment_form.html"
    detail_fragment = "study/attachment_item.html"
    list_fragment = "study/_attachment_list.html"

    @action(permission=can_view)
    def read(self, request: HttpRequest, *args, **kwargs):
        return render(request, self.detail_fragment, self.get_context_data())

    @action(methods=("get", "post"), permission=can_edit)
    def create(self, request: HttpRequest, *args, **kwargs):
        template = self.list_fragment
        if request.method == "POST":
            form = forms.AttachmentForm(request.POST, request.FILES, parent=request.item.parent)
            if form.is_valid():
                self.perform_create(request.item, form)
                template = self.detail_fragment
        else:
            form = forms.AttachmentForm(parent=request.item.parent)
        context = self.get_context_data(form=form)
        context["attachments"] = models.Attachment.objects.get_attachments(
            request.item.parent, False
        )
        return render(request, template, context)

    @action(methods=("get", "post"), permission=can_edit)
    def delete(self, request: HttpRequest, *args, **kwargs):
        if request.method == "POST":
            self.perform_delete(request.item)
            return self.str_response()
        return render(request, self.detail_fragment, self.get_context_data())


class AttachmentRead(BaseDetail):
    model = models.Attachment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.assessment.user_is_part_of_team(self.request.user):
            return HttpResponseRedirect(self.object.attachment.url)
        else:
            raise PermissionDenied

            
class AttachmentList(BaseList):
    model = models.Attachment
    parent_model = models.Study
    parent_template_name = "parent"
    template_name = "study/_attachment_list.html"
    object_list = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = models.Attachment.objects.get_attachments(
            self.parent, not context["obj_perms"]["edit"]
        )
        return context

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = self.get_context_data()
        return render(request, "study/_attachment_list.html", context)
