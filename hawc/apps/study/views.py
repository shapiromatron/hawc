from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django.views.generic.edit import UpdateView

from ..assessment.forms import CommunicationForm
from ..assessment.models import Assessment, Communication
from ..common.crumbs import Breadcrumb
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

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment.id)


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
            "attachments": self.object.get_attachments_dict() if attachments_viewable else None,
        }
        context["user_is_team_member_or_higher"] = self.assessment.user_is_team_member_or_higher(
            self.request.user._wrapped
        )
        try:
            communication_message = Communication.objects.get(object_id=self.object.id).message
        except Communication.DoesNotExist:
            communication_message = ""
        context["Communication"] = communication_message
        return context


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


class AttachmentRead(BaseDetail):
    model = models.Attachment

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.assessment.user_is_part_of_team(self.request.user):
            return HttpResponseRedirect(self.object.attachment.url)
        else:
            raise PermissionDenied


class EditabilityUpdate(BaseUpdate):
    # TODO - change to DRF or add new option to standard StudyUpdate view

    model = models.Study

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.assessment.user_can_edit_assessment(self.request.user):
            probe = kwargs["updated_value"]
            if probe == "True":
                self.object.editable = True
            elif probe == "False":
                self.object.editable = False
            else:
                raise Exception("invalid input value")

            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())
        else:
            raise PermissionDenied


# Communication view
class CommunicationUpdate(UpdateView):
    template_name = "study/communication_update.html"
    model = Communication
    form_class = CommunicationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_type = ContentType.objects.get(app_label="study", model="study")
        study = content_type.get_object_for_this_type(id=(self.object.object_id))
        context["assessment"] = study.get_assessment()
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Communication Update",
            extras=[
                Breadcrumb.from_object(context["assessment"]),
                Breadcrumb(
                    name="Study " + str(study), url=reverse("study:detail", args=(study.id,))
                ),
            ],
        )
        return context

    def get_object(self, queryset=None):
        content_type = ContentType.objects.get(app_label="study", model="communication")
        import pdb

        pdb.set_trace()
        obj, created = Communication.objects.get_or_create(
            content_type=content_type, object_id=self.kwargs["pk"]
        )
        return obj

    def post(self, request, *args, **kwargs):
        instance = Communication.objects.get(object_id=self.kwargs["pk"])
        if instance is not None:
            form = CommunicationForm(request.POST, instance=instance)
        else:
            form = CommunicationForm(request.POST)
        form.save()
        return HttpResponseRedirect(reverse("study:detail", args=[self.kwargs["pk"]]))
