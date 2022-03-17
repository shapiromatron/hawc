import abc
import logging
from typing import Any, Callable, Iterable, List, Optional
from urllib.parse import urlparse

import reversion
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import EmptyResultSet, PermissionDenied
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import Resolver404, resolve, reverse
from django.utils.decorators import method_decorator
from django.utils.http import is_same_domain
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ..assessment.models import Assessment, BaseEndpoint, Log, TimeSpentEditing
from .crumbs import Breadcrumb
from .helper import WebappConfig, tryParseInt

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("hawc.audit.change")


def beta_tester_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in and a beta-tester, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_beta_tester(),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def get_referrer(request: HttpRequest, default: str) -> str:
    """Return the `referer` [sic] attribute if it's a valid HAWC site, otherwise use default.

    `Referer` [sic] header could be malicious or may include injected code. Only return the
    value if the path can be resolved in HAWC.

    Args:
        request (HttpRequest): the http request

    Returns:
        str: A valid URL, with query params dropped
    """
    url = request.META.get("HTTP_REFERER")
    this_host = request.get_host()

    if default.startswith("https"):
        default_url = default
    else:
        default_url = f"https://{this_host}{default}"

    if url is None:
        return default_url

    parsed_url = urlparse(url)
    if not is_same_domain(parsed_url.netloc, this_host):
        return default_url

    try:
        _ = resolve(parsed_url.path)
    except Resolver404:
        return default_url

    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


def create_object_log(verb: str, obj, assessment_id: int, user_id: int):
    """
    Create an object log for a given object and associate a reversion instance if it exists.

    Calling this method should be wrapped in a transaction.

    Args:
        verb (str): the action being performed
        obj (Any): the object
        assessment_id (int): the object assessment id
        user_id (int): the user id
    """
    # Log action
    meta = obj._meta
    log_message = f'{verb} {meta.app_label}.{meta.model_name} #{obj.id}: "{obj}"'
    log = Log.objects.create(
        assessment_id=assessment_id, user_id=user_id, message=log_message, content_object=obj,
    )
    # Associate log with reversion
    comment = (
        f"{reversion.get_comment()}, Log {log.id}" if reversion.get_comment() else f"Log {log.id}"
    )
    audit_logger.info(f"[{log.id}] assessment-{assessment_id} user-{user_id} {log_message}")
    reversion.set_comment(comment)


def bulk_create_object_log(verb: str, obj_list: Iterable[Any], user_id: int):
    """
    Create an object log for each item in list and  associate a reversion instance if it exists.

    Calling this method should be wrapped in a transaction.

    Args:
        verb (str): the action being performed
        obj_list (Any): an iterable of
        assessment_id (int): the object assessment id
        user_id (int): the user id
    """
    objects = []
    for obj in obj_list:
        # Log action
        assessment_id = obj.get_assessment().id
        meta = obj._meta
        log_message = f'{verb} {meta.app_label}.{meta.model_name} #{obj.id}: "{obj}"'
        objects.append(
            Log(
                assessment_id=assessment_id,
                user_id=user_id,
                message=log_message,
                content_object=obj,
            )
        )
    logs = Log.objects.bulk_create(objects)

    # Associate log with reversion
    log_ids = ",".join(map(str, [log.id for log in logs]))
    for log in logs:
        comment = (
            f"{reversion.get_comment()}, Logs {log_ids}"
            if reversion.get_comment()
            else f"Logs {log_ids}"
        )
        audit_logger.info(
            f"[bulk {log_ids}] assessment-{logs[0].get_assessment().id} user-{user_id}"
        )
        reversion.set_comment(comment)


class MessageMixin:
    """
    Make it easy to display notification messages when using Class Based Views.
    Originally from http://stackoverflow.com/questions/5531258/
    """

    def send_message(self):
        logger.debug("MessagingMixin called")
        if self.success_message is not None:
            messages.success(self.request, self.success_message, extra_tags="alert alert-success")

    def delete(self, request, *args, **kwargs):
        self.send_message()
        return super().delete(request, *args, **kwargs)

    def form_valid(self, form):
        self.send_message()
        return super().form_valid(form)


class CloseIfSuccessMixin:
    """
    Mixin designed to close-window if form executes successfully.
    """

    def get_success_url(self):
        return reverse("assessment:close_window")


class LoginRequiredMixin:
    """
    A mixin requiring a user to be logged in.
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AssessmentPermissionsMixin:
    """
    Mixin to check permissions for an object of interest to determine if a user
    is able to view and delete the object. Will return an object or issue an
    HTTP 403 error. Will also return a set of template tags {{ obj_perms }}
    for displaying page. Note that this for all objects which are controlled
    by the assessment object but not including the assessment object.
    """

    def deny_for_locked_study(self, user, assessment, obj):
        # determine relevant study for a given object, and then checks its editable status.
        # If not set, raises a PermissionDenied.
        study_editability = self.check_study_editability(user, assessment, obj)
        if study_editability is not None:
            if study_editability is False:
                raise PermissionDenied

    def check_study_editability(self, user, assessment, obj):
        # TODO - investigate refactoring only in the case where an object is being mutated; not read
        # (will reduce db query load for getting study for all objects)
        # TODO - add unit tests
        # retrieve the related study from this instance
        # could also do this by defining some kind of base class that Study, Experiment, etc.
        # inherit from, and define the get_study method on there. Then we just
        # check an "is-a" instead of looking for the attribute manually.
        study = None
        if hasattr(obj, "get_study"):
            study = obj.get_study()

        if assessment.user_can_edit_object(user):
            if study:
                return study.user_can_edit_study(assessment, user)
            return None
        else:
            return False

    # could be a model element (Study, Endpoint, etc.) or a view to create a new one (EndpointCreate, etc.)
    def get_contextual_object_for_study_editability_check(self):
        if hasattr(self, "object") and self.object is not None:
            # looking at a specific object directly
            return self.object
        elif hasattr(self, "parent") and self.parent is not None:
            # looking at a Create view; can look at the parent/container object to determine study editable status
            return self.parent
        else:
            return None

    def permission_check_user_can_view(self):
        logger.debug("Permissions checked")
        if not self.assessment.user_can_view_object(self.request.user):
            raise PermissionDenied

    def permission_check_user_can_edit(self):
        logger.debug("Permissions checked")
        if self.model == Assessment:
            canEdit = self.assessment.user_can_edit_assessment(self.request.user)
        else:
            self.deny_for_locked_study(
                self.request.user,
                self.assessment,
                self.get_contextual_object_for_study_editability_check(),
            )
            canEdit = self.assessment.user_can_edit_object(self.request.user)
        if not canEdit:
            raise PermissionDenied

    def get_object(self, **kwargs):
        """
        Check to make sure user can view object
        """
        obj = kwargs.get("object")
        if not obj:
            obj = super().get_object(**kwargs)

        if not hasattr(self, "assessment"):
            self.assessment = obj.get_assessment()

        if self.crud == "Read":
            perms = self.assessment.user_can_view_object(self.request.user)
        else:
            if self.model == Assessment:
                perms = self.assessment.user_can_edit_assessment(self.request.user)
            else:
                self.deny_for_locked_study(self.request.user, self.assessment, obj)
                perms = self.assessment.user_can_edit_object(self.request.user)

        logger.debug("Permissions checked")
        if perms:
            return obj
        else:
            raise PermissionDenied

    def get_queryset(self):
        """
        IF attempting to use for permissions checking, requires a
        self.assessment parameter in class with the assessment to check
        permissions for.
        """
        queryset = super().get_queryset()
        if not hasattr(self, "assessment"):
            # get_object calls get_queryset; thus we must be careful to check
            # the correct object
            return queryset
        else:
            # IF, the view has a self.assessment identified, this will check
            # to ensure that a user is allowed to perform the selected actions.
            #
            # TODO: might be preferred to check the get_assessment function with
            # a user, and ensure that get_assessment is called for ALL models
            # with assessment permissions mixin
            #
            if self.crud == "Read":
                perms = self.assessment.user_can_view_object(self.request.user)
            else:
                if self.model == Assessment:
                    perms = self.assessment.user_can_edit_assessment(self.request.user)
                else:
                    obj = queryset.first()
                    if obj is None:
                        raise EmptyResultSet(
                            "Cannot determine if objects should be locked for editing"
                        )
                    self.deny_for_locked_study(self.request.user, self.assessment, obj)
                    perms = self.assessment.user_can_edit_object(self.request.user)
            logger.debug("Permissions checked")
            if perms:
                return queryset
            else:
                raise PermissionDenied

    def get_obj_perms(self):
        if not hasattr(self, "assessment"):
            logger.error("unable to determine object permissions")
            return {"view": False, "edit": False, "edit_assessment": False}

        logger.debug("Permissions added")
        user_perms = self.assessment.user_permissions(self.request.user)

        contextual_obj = self.get_contextual_object_for_study_editability_check()
        study_perm_check = self.check_study_editability(
            self.request.user, self.assessment, contextual_obj
        )
        if study_perm_check is not None:
            user_perms["edit"] = study_perm_check

        return user_perms


class TimeSpentOnPageMixin:
    def get(self, request, *args, **kwargs):
        TimeSpentEditing.set_start_time(
            self.request.session.session_key, self.request.path,
        )
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        response = super().get_success_url()
        TimeSpentEditing.add_time_spent_job(
            self.request.session.session_key, self.request.path, self.object, self.assessment.id,
        )
        return response


class ProjectManagerOrHigherMixin:
    """
    Mixin for project-manager access to page.
    Requires a get_assessment method; checked for all HTTP verbs.
    """

    @abc.abstractmethod
    def get_assessment(self, request, *args, **kwargs):
        raise NotImplementedError("get_assessment requires implementation")

    def dispatch(self, request, *args, **kwargs):
        self.assessment = self.get_assessment(request, *args, **kwargs)
        logger.debug("Permissions checked")
        if not self.assessment.user_can_edit_assessment(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assessment"] = self.assessment
        return context


class TeamMemberOrHigherMixin:
    """
    Mixin for team-member access to page.
    Requires a get_assessment method; checked for all HTTP verbs.
    """

    @abc.abstractmethod
    def get_assessment(self, request, *args, **kwargs):
        raise NotImplementedError("get_assessment requires implementation")

    def dispatch(self, request, *args, **kwargs):
        self.assessment = self.get_assessment(request, *args, **kwargs)
        logger.debug("Permissions checked")
        if not self.assessment.user_can_edit_object(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assessment"] = self.assessment
        return context


class CanCreateMixin:
    """
    Checks to make sure that the user has appropriate permissions before adding
    a new object to the assessment. Requires a self.assessment variable to be
    created before rendering.
    """

    def user_can_create_object(self, assessment):
        """
        If person is superuser or assessment is editable and user is a project
        manager or team member.
        """
        logger.debug("Permissions checked")
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_anonymous:
            return False
        else:
            return (assessment.editable is True) and (
                (self.request.user in assessment.project_manager.all())
                or (self.request.user in assessment.team_members.all())
            )

    def get(self, request, *args, **kwargs):
        if self.user_can_create_object(self.assessment):
            return super().get(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if self.user_can_create_object(self.assessment):
            return super().post(request, *args, **kwargs)
        else:
            raise PermissionDenied


class CopyAsNewSelectorMixin:

    copy_model = None  # required
    template_name_suffix = "_copy_selector"

    def get_related_id(self):
        return self.object.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # prevents copy from locked studies
        if context["obj_perms"]["edit"] is False:
            raise PermissionDenied

        related_id = self.get_related_id()
        context["form"] = self.form_class(parent_id=related_id)
        context["breadcrumbs"].append(
            Breadcrumb(name=f"Clone {self.copy_model._meta.verbose_name}")
        )
        return context

    def get_template_names(self):
        if self.template_name is not None:
            name = self.template_name
        else:
            name = "%s/%s%s.html" % (
                self.copy_model._meta.app_label,
                self.copy_model._meta.object_name.lower(),
                self.template_name_suffix,
            )
        return [name]


class WebappMixin:
    """Mixin to startup a javascript single-page application"""

    get_app_config: Optional[Callable[[RequestContext], WebappConfig]] = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_app_config:
            context["config"] = self.get_app_config(context).dict()
        return context


# Base HAWC views
class BaseDetail(WebappMixin, AssessmentPermissionsMixin, DetailView):
    crud = "Read"
    breadcrumb_active_name: Optional[str] = None

    def get_breadcrumbs(self) -> List[Breadcrumb]:
        return Breadcrumb.build_assessment_crumbs(self.request.user, self.object)

    def get_context_data(self, **kwargs):
        extras = {
            "assessment": self.assessment,
            "crud": self.crud,
            "obj_perms": super().get_obj_perms(),
            "breadcrumbs": self.get_breadcrumbs(),
        }
        for key, value in extras.items():
            if key not in kwargs:
                kwargs[key] = value
        context = super().get_context_data(**kwargs)
        if self.breadcrumb_active_name:
            context["breadcrumbs"].append(Breadcrumb(name=self.breadcrumb_active_name))
        return context


class BaseDelete(WebappMixin, AssessmentPermissionsMixin, MessageMixin, DeleteView):
    crud = "Delete"

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.permission_check_user_can_edit()
        success_url = self.get_success_url()
        self.create_log(self.object)
        self.object.delete()
        self.send_message()
        return HttpResponseRedirect(success_url)

    def create_log(self, obj):
        create_object_log("Deleted", obj, self.assessment.id, self.request.user.id)

    def get_cancel_url(self) -> str:
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        extras = {
            "assessment": self.assessment,
            "crud": self.crud,
            "obj_perms": super().get_obj_perms(),
            "cancel_url": self.get_cancel_url(),
            "breadcrumbs": self.get_breadcrumbs(),
        }
        for key, value in extras.items():
            if key not in kwargs:
                kwargs[key] = value
        context = super().get_context_data(**kwargs)
        return context

    def get_breadcrumbs(self) -> List[Breadcrumb]:
        crumbs = Breadcrumb.build_assessment_crumbs(self.request.user, self.object)
        crumbs.append(Breadcrumb(name="Delete"))
        return crumbs


class BaseUpdate(
    WebappMixin, TimeSpentOnPageMixin, AssessmentPermissionsMixin, MessageMixin, UpdateView
):
    crud = "Update"

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        self.post_object_save(form)  # add hook for post-object save
        self.create_log(self.object)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def create_log(self, obj):
        create_object_log("Updated", obj, self.assessment.id, self.request.user.id)

    def post_object_save(self, form):
        pass

    def get_context_data(self, **kwargs):
        extras = {
            "assessment": self.assessment,
            "crud": self.crud,
            "obj_perms": super().get_obj_perms(),
            "breadcrumbs": self.get_breadcrumbs(),
        }
        for key, value in extras.items():
            if key not in kwargs:
                kwargs[key] = value
        context = super().get_context_data(**kwargs)
        return context

    def get_breadcrumbs(self) -> List[Breadcrumb]:
        crumbs = Breadcrumb.build_assessment_crumbs(self.request.user, self.object)
        crumbs.append(Breadcrumb(name="Update"))
        return crumbs


class BaseCreate(
    WebappMixin, TimeSpentOnPageMixin, AssessmentPermissionsMixin, MessageMixin, CreateView
):
    parent_model = None  # required
    parent_template_name: Optional[str] = None  # required
    crud = "Create"

    def dispatch(self, *args, **kwargs):
        self.parent = get_object_or_404(self.parent_model, pk=kwargs["pk"])
        self.assessment = self.parent.get_assessment()
        self.permission_check_user_can_edit()
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # all inputs require a parent field
        kwargs["parent"] = self.parent

        # check if we have an object-template to be used
        pk = tryParseInt(self.request.GET.get("initial"), -1)

        if pk > 0:
            initial = self.model.objects.filter(pk=pk).first()
            if initial and initial.get_assessment() in Assessment.objects.get_viewable_assessments(
                self.request.user
            ):
                kwargs["initial"] = model_to_dict(initial)

        return kwargs

    def get_context_data(self, **kwargs):
        extras = {
            "assessment": self.assessment,
            "crud": self.crud,
            "obj_perms": super().get_obj_perms(),
            "breadcrumbs": self.get_breadcrumbs(),
        }
        for key, value in extras.items():
            if key not in kwargs:
                kwargs[key] = value
        context = super().get_context_data(**kwargs)
        context[self.parent_template_name] = self.parent
        return context

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        self.post_object_save(form)  # add hook for post-object save
        self.create_log(self.object)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def create_log(self, obj):
        create_object_log("Created", obj, self.assessment.id, self.request.user.id)

    def post_object_save(self, form):
        pass

    def get_breadcrumbs(self) -> List[Breadcrumb]:
        crumbs = Breadcrumb.build_assessment_crumbs(self.request.user, self.parent)
        crumbs.append(Breadcrumb(name=f"Create {self.model._meta.verbose_name}"))
        return crumbs


class BaseList(WebappMixin, AssessmentPermissionsMixin, ListView):
    """
    Basic view that shows a list of objects given
    """

    parent_model = None  # required
    parent_template_name = None
    crud = "Read"
    breadcrumb_active_name: Optional[str] = None

    def dispatch(self, *args, **kwargs):
        self.parent = get_object_or_404(self.parent_model, pk=kwargs["pk"])
        self.assessment = self.parent.get_assessment()
        self.permission_check_user_can_view()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        extras = {
            "assessment": self.assessment,
            "crud": self.crud,
            "obj_perms": super().get_obj_perms(),
            "breadcrumbs": self.get_breadcrumbs(),
        }
        for key, value in extras.items():
            if key not in kwargs:
                kwargs[key] = value
        context = super().get_context_data(**kwargs)
        if self.parent_template_name:
            context[self.parent_template_name] = self.parent
        return context

    def get_breadcrumbs(self) -> List[Breadcrumb]:
        crumbs = Breadcrumb.build_assessment_crumbs(self.request.user, self.parent)
        name = (
            self.breadcrumb_active_name
            or str(getattr(self.model._meta, "verbose_name_plural", self.model)).title()
        )
        crumbs.append(Breadcrumb(name=name))
        return crumbs


class BaseCreateWithFormset(BaseCreate):
    """
    Create view with both a single form and formset. Adds three new options:

    - formset_factory: required to load POST data into factory. Formset factory method.
    - post_object_save: method for modifying formset after form is saved but before formset. No return.
    - build_initial_formset_factory: method for returning initial formset factory. Returns formset_factory
    """

    formset_factory = None  # required

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset_factory(data=self.request.POST, **self.get_formset_kwargs())
        self.pre_validate(form, formset)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def get_formset_kwargs(self):
        return {}

    @transaction.atomic
    def form_valid(self, form, formset):
        self.object = form.save()
        self.post_object_save(form, formset)
        formset.save()
        self.post_formset_save(form, formset)
        self.create_log(self.object)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        if "formset" not in kwargs:
            kwargs["formset"] = self.build_initial_formset_factory()
        return super().get_context_data(**kwargs)

    def pre_validate(self, form, formset):
        pass

    def post_object_save(self, form, formset):
        pass

    def post_formset_save(self, form, formset):
        pass

    def build_initial_formset_factory(self):
        # Returns initial formset factory
        raise NotImplementedError("Method should be overridden to return a formset factory")


class BaseUpdateWithFormset(BaseUpdate):
    """
    Update view with both a single form and formset. Adds three new options:

    - formset_factory: required to load POST data into factory. Formset factory method.
    - post_objet_save: method for modifying formset after form is saved but before formset. No return.
    - build_initial_formset_factory: method for returning initial formset factory. Returns formset_factory
    """

    formset_factory = None  # required

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset_factory(data=self.request.POST, **self.get_formset_kwargs())
        self.pre_validate(form, formset)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def get_formset_kwargs(self):
        return {}

    @transaction.atomic
    def form_valid(self, form, formset):
        self.object = form.save()
        self.post_object_save(form, formset)
        formset.save()
        self.post_formset_save(form, formset)
        self.create_log(self.object)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def pre_validate(self, form, formset):
        pass

    def post_object_save(self, form, formset):
        pass

    def post_formset_save(self, form, formset):
        pass

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def build_initial_formset_factory(self):
        # Returns initial formset factory
        raise NotImplementedError("Method should be overridden to return a formset factory")

    def get_context_data(self, **kwargs):
        if "formset" not in kwargs:
            kwargs["formset"] = self.build_initial_formset_factory()
        return super().get_context_data(**kwargs)


class BaseEndpointFilterList(BaseList):
    parent_model = Assessment

    def get_paginate_by(self, qs) -> int:
        value = self.request.GET.get("paginate_by")
        return tryParseInt(value, default=25, min_value=10, max_value=500)

    def get(self, request, *args, **kwargs):
        if len(self.request.GET) > 0:
            self.form = self.form_class(self.request.GET, assessment=self.assessment)
        else:
            self.form = self.form_class(assessment=self.assessment)
        return super().get(request, *args, **kwargs)

    def get_query(self, perms):
        """
        query = Q(relation__to__assessment=self.assessment)
        if not perms['edit']:
            query &= Q(study__published=True)
        return query
        """
        pass

    def get_queryset(self):
        perms = super().get_obj_perms()
        order_by = None

        query = self.get_query(perms)

        if self.form.is_valid():
            query &= self.form.get_query()
            order_by = self.form.get_order_by()

        ids = (
            self.model.objects.filter(query)
            .order_by("id")
            .distinct("id")
            .values_list("id", flat=True)
        )

        qs = self.model.objects.filter(id__in=ids)

        if order_by:
            qs = qs.order_by(order_by)

        return qs

    def get_context_data(self, **kwargs):
        kwargs["form"] = self.form
        context = super().get_context_data(**kwargs)
        if "config" not in context:  # TODO - remove this case; implement #507
            context["config"] = {
                "items": self.model.get_qs_json(context["object_list"], json_encode=False)
            }
        return context


class HeatmapBase(BaseList):
    parent_model = Assessment
    model = BaseEndpoint
    template_name = "common/heatmap.html"
    heatmap_data_class: str = ""
    heatmap_data_url: str = ""
    heatmap_view_title: str = ""

    def get_template_names(self):
        return [self.template_name]

    def get_context_data(self, **kwargs):
        kwargs["breadcrumbs"] = [
            Breadcrumb.build_root(self.request.user),
            Breadcrumb.from_object(self.assessment),
            Breadcrumb(
                name="Endpoints",
                url=reverse("assessment:endpoint_list", args=(self.assessment.id,)),
            ),
            Breadcrumb(name=self.heatmap_view_title),
        ]
        return super().get_context_data(**kwargs)

    def get_app_config(self, context) -> WebappConfig:
        url_args = (
            "?unpublished=true"
            if self.request.GET.get("unpublished", "false").lower() == "true"
            else ""
        )
        can_edit = context["obj_perms"]["edit"]
        create_url = reverse("summary:visualization_create", args=(self.assessment.id, 6))
        return WebappConfig(
            app="heatmapTemplateStartup",
            data=dict(
                assessment=str(self.assessment),
                data_class=self.heatmap_data_class,
                data_url=reverse(self.heatmap_data_url, args=(self.assessment.id,)) + url_args,
                clear_cache_url=self.assessment.get_clear_cache_url() if can_edit else None,
                create_visual_url=create_url if can_edit else None,
            ),
        )
