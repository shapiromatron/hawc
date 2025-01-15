import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import wraps
from typing import Any
from urllib.parse import urlparse

import reversion
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.context_processors import csrf
from django.urls import Resolver404, resolve, reverse
from django.utils.decorators import method_decorator
from django.utils.http import is_same_domain
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ..assessment.constants import AssessmentViewPermissions
from ..assessment.models import Assessment, BaseEndpoint, Log, TimeSpentEditing
from .crumbs import Breadcrumb
from .filterset import BaseFilterSet
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
    url = request.headers.get("referer")
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


def add_csrf(obj: dict, request: HttpRequest) -> dict:
    """Add CSRF token to context object as the key `csrf`."""
    obj["csrf"] = str(csrf(request)["csrf_token"])
    return obj


def create_object_log(
    verb: str, obj, assessment_id: int | None, user_id: int, log_message: str = ""
):
    """
    Create an object log for a given object and associate a reversion instance if it exists.

    Calling this method should be wrapped in a transaction.

    Args:
        verb (str): the action being performed
        obj (Any): the object
        assessment_id (int|None): the object assessment id
        user_id (int): the user id
        log_message (str): override for custom message
    """
    # Log action
    meta = obj._meta
    if not log_message:
        log_message = f'{verb} {meta.app_label}.{meta.model_name} #{obj.id}: "{obj}"'
    log = Log.objects.create(
        assessment_id=assessment_id,
        user_id=user_id,
        message=log_message,
        content_object=obj,
    )
    # Associate log with reversion
    comment = (
        f"{reversion.get_comment()}, Log {log.id}" if reversion.get_comment() else f"Log {log.id}"
    )
    audit_logger.info(f"[{log.id}] assessment-{assessment_id} user-{user_id} {log_message}")
    reversion.set_comment(comment)


def bulk_create_object_log(verb: str, obj_list: Iterable[Any], user_id: int):
    """
    Create an object log for each item modified in list.

    Calling this method should be wrapped in a transaction. Does not associate a reversion; bulk
    updates are not typically tracked in reversions.

    Args:
        verb (str): the action being performed
        obj_list (Any): an iterable of an object type
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
    Log.objects.bulk_create(objects)


class MessageMixin:
    """
    Make it easy to display notification messages when using Class Based Views.
    Originally from http://stackoverflow.com/questions/5531258/
    """

    def send_message(self):
        logger.debug("MessagingMixin called")
        if self.success_message is not None:
            messages.success(self.request, self.success_message, extra_tags="alert alert-success")

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

    assessment_permission: AssessmentViewPermissions

    def deny_for_locked_study(self, user, assessment, obj):
        # determine relevant study for a given object, and then checks its editable status.
        # If not set, raises a PermissionDenied.
        study_editability = self.check_study_editability(user, assessment, obj)
        if study_editability is False:
            raise PermissionDenied()

    def deny_for_locked_assessment(self, assessment):
        if not assessment.editable:
            raise PermissionDenied()

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

    def get_object_for_study_editability_check(self):
        # return object if one exists (detail, update, delete)
        if object := getattr(self, "object", None):
            return object

        # return parent if one exists (create)
        if parent := getattr(self, "parent", None):
            return parent

        raise ValueError("Cannot determine permissions object")

    def check_queryset_study_editability(self, queryset):
        first_object = queryset.first()
        if first_object is None:
            raise ValueError("Cannot determine if objects should be locked for editing")
        self.deny_for_locked_study(self.request.user, self.assessment, first_object)

    def get_object(self, **kwargs):
        obj = kwargs.get("object") or super().get_object(**kwargs)

        if not hasattr(self, "assessment"):
            self.assessment = obj.get_assessment()

        permission_checked = False
        user = self.request.user
        match self.assessment_permission:
            case AssessmentViewPermissions.PROJECT_MANAGER:
                permission_checked = self.assessment.user_is_project_manager_or_higher(user)
            case AssessmentViewPermissions.PROJECT_MANAGER_EDITABLE:
                self.deny_for_locked_assessment(self.assessment)
                permission_checked = self.assessment.user_is_project_manager_or_higher(user)
            case AssessmentViewPermissions.TEAM_MEMBER:
                permission_checked = self.assessment.user_is_team_member_or_higher(user)
            case AssessmentViewPermissions.TEAM_MEMBER_EDITABLE:
                self.deny_for_locked_study(user, self.assessment, obj)
                permission_checked = self.assessment.user_can_edit_object(user)
            case AssessmentViewPermissions.VIEWER:
                permission_checked = self.assessment.user_can_view_object(user)

        if not permission_checked:
            raise PermissionDenied()
        logger.debug("Permissions checked: object")

        return obj

    def get_queryset(self):
        queryset = super().get_queryset()

        # don't queryset if we have `get_object`; assume we check there
        if isinstance(self, SingleObjectMixin):
            return queryset

        if not hasattr(self, "assessment"):
            raise ValueError("No assessment object; required to check permission")

        permission_checked = False
        user = self.request.user
        match self.assessment_permission:
            case AssessmentViewPermissions.PROJECT_MANAGER:
                permission_checked = self.assessment.user_is_project_manager_or_higher(user)
            case AssessmentViewPermissions.PROJECT_MANAGER_EDITABLE:
                self.deny_for_locked_assessment(self.assessment)
                permission_checked = self.assessment.user_is_project_manager_or_higher(user)
            case AssessmentViewPermissions.TEAM_MEMBER:
                permission_checked = self.assessment.user_is_team_member_or_higher(user)
            case AssessmentViewPermissions.TEAM_MEMBER_EDITABLE:
                self.check_queryset_study_editability(queryset)
                permission_checked = self.assessment.user_can_edit_object(user)
            case AssessmentViewPermissions.VIEWER:
                permission_checked = self.assessment.user_can_view_object(user)
        if not permission_checked:
            raise PermissionDenied()
        logger.debug("Permissions checked: queryset")

        return queryset

    def get_obj_perms(self):
        if not hasattr(self, "assessment"):
            raise ValueError("Unable to determine object permissions")

        logger.debug("Permissions added")
        user_perms = self.assessment.user_permissions(self.request.user)

        object = self.get_object_for_study_editability_check()
        study_perm_check = self.check_study_editability(self.request.user, self.assessment, object)
        if study_perm_check is not None:
            user_perms["edit"] = study_perm_check

        return user_perms


class TimeSpentOnPageMixin:
    def get(self, request, *args, **kwargs):
        TimeSpentEditing.set_start_time(request)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        TimeSpentEditing.add_time_spent_job(self.request, self.object, self.assessment.id)
        return super().get_success_url()


class WebappMixin:
    """Mixin to startup a javascript single-page application"""

    get_app_config: Callable[[RequestContext], WebappConfig] | None = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_app_config:
            context["config"] = self.get_app_config(context).model_dump()
        return context


# Base HAWC views
class BaseDetail(WebappMixin, AssessmentPermissionsMixin, DetailView):
    crud = "Read"
    breadcrumb_active_name: str | None = None
    assessment_permission = AssessmentViewPermissions.VIEWER

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        return Breadcrumb.build_assessment_crumbs(self.request.user, self.object)

    def get_context_data(self, **kwargs):
        extras = {
            "assessment": self.assessment,
            "crud": self.crud,
            "obj_perms": super().get_obj_perms(),
            "breadcrumbs": self.get_breadcrumbs(),
        }
        for key, value in extras.items():
            kwargs.setdefault(key, value)
        context = super().get_context_data(**kwargs)
        if self.breadcrumb_active_name:
            context["breadcrumbs"].append(Breadcrumb(name=self.breadcrumb_active_name))
        return context


class BaseDelete(WebappMixin, AssessmentPermissionsMixin, MessageMixin, DeleteView):
    crud = "Delete"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE
    # remove `delete` from method names
    # delete method CBV different than post; we only need to implement POST
    # - https://github.com/django/django/blob/c3d7a71f836f7cfe8fa90dd9ae95b37b660d5aae/django/views/generic/edit.py#L220
    # - https://github.com/django/django/blob/c3d7a71f836f7cfe8fa90dd9ae95b37b660d5aae/django/views/generic/edit.py#L250
    http_method_names = ["get", "post", "put", "patch", "head", "options", "trace"]

    @transaction.atomic
    def form_valid(self, form):
        self.check_delete()
        success_url = self.get_success_url()
        self.create_log(self.object)
        self.object.delete()
        self.send_message()
        return HttpResponseRedirect(success_url)

    def check_delete(self):
        """Additional permission checks for DELETE requests; not GET requests.

        This may be useful for situations where you need to explain to a user why they cannot
        delete an object in the GET, and if they try, we can raise an exception here.
        """
        pass

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
            kwargs.setdefault(key, value)
        context = super().get_context_data(**kwargs)
        return context

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        crumbs = Breadcrumb.build_assessment_crumbs(self.request.user, self.object)
        crumbs.append(Breadcrumb(name="Delete"))
        return crumbs


class BaseUpdate(
    WebappMixin, TimeSpentOnPageMixin, AssessmentPermissionsMixin, MessageMixin, UpdateView
):
    crud = "Update"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE

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
            kwargs.setdefault(key, value)
        context = super().get_context_data(**kwargs)
        return context

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        crumbs = Breadcrumb.build_assessment_crumbs(self.request.user, self.object)
        crumbs.append(Breadcrumb(name="Update"))
        return crumbs


class BaseCreate(
    WebappMixin, TimeSpentOnPageMixin, AssessmentPermissionsMixin, MessageMixin, CreateView
):
    parent_model: type[models.Model]
    parent_template_name: str
    crud = "Create"
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE

    def dispatch(self, *args, **kwargs):
        parent = get_object_or_404(self.parent_model, pk=kwargs["pk"])
        self.parent = self.get_object(object=parent)  # call for assessment permissions check
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # all inputs require a parent field
        kwargs["parent"] = self.parent

        # check if we have an object-template to be used
        pk = tryParseInt(self.request.GET.get("initial"), -1)

        if pk > 0:
            initial = self.model.objects.filter(pk=pk).first()
            if initial and initial.get_assessment() in Assessment.objects.all().user_can_view(
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
            kwargs.setdefault(key, value)
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

    def get_breadcrumbs(self) -> list[Breadcrumb]:
        crumbs = Breadcrumb.build_assessment_crumbs(self.request.user, self.parent)
        crumbs.append(Breadcrumb(name=f"Create {self.model._meta.verbose_name}"))
        return crumbs


class BaseCopyForm(BaseUpdate):
    copy_model: type[models.Model]
    breadcrumb_name: str = ""
    template_name = "common/copy_selector.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw.pop("instance")
        kw["parent"] = self.object
        return kw

    def form_valid(self, form):
        return HttpResponseRedirect(form.get_success_url())

    def get_template_names(self) -> list[str]:
        if self.template_name:
            return [self.template_name]
        model_meta = self.copy_model._meta
        return [f"{model_meta.app_label}/{model_meta.object_name.lower()}_copy_selector.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"][-1] = Breadcrumb(
            name=self.breadcrumb_name or f"Copy {self.copy_model._meta.verbose_name}"
        )
        return context


class BaseList(WebappMixin, AssessmentPermissionsMixin, ListView):
    """
    Basic view that shows a list of objects given
    """

    parent_model = None  # required
    parent_template_name = None
    crud = "Read"
    breadcrumb_active_name: str | None = None
    assessment_permission = AssessmentViewPermissions.VIEWER

    def dispatch(self, *args, **kwargs):
        self.parent = get_object_or_404(self.parent_model, pk=kwargs["pk"])
        self.assessment = self.parent.get_assessment()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        extras = {
            "assessment": self.assessment,
            "crud": self.crud,
            "obj_perms": super().get_obj_perms(),
            "breadcrumbs": self.get_breadcrumbs(),
        }
        for key, value in extras.items():
            kwargs.setdefault(key, value)
        context = super().get_context_data(**kwargs)
        if self.parent_template_name:
            context[self.parent_template_name] = self.parent
        return context

    def get_breadcrumbs(self) -> list[Breadcrumb]:
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


class FilterSetMixin:
    filterset_class: type[BaseFilterSet]
    paginate_by = 25

    def get_paginate_by(self, queryset) -> int:
        form = self.filterset.form
        value = (
            form.cleaned_data.get("paginate_by")
            if hasattr(form, "cleaned_data")
            else self.paginate_by
        )
        return tryParseInt(value, default=self.paginate_by, min_value=10, max_value=500)

    def get_filterset_kwargs(self):
        return dict(
            data=self.request.GET,
            queryset=super().get_queryset(),
            request=self.request,
            form_kwargs=self.get_filterset_form_kwargs(),
        )

    def get_filterset_form_kwargs(self):
        return {}

    @property
    def filterset(self):
        if not hasattr(self, "_filterset"):
            self._filterset = self.filterset_class(**self.get_filterset_kwargs())
        return self._filterset

    def get_queryset(self):
        return self.filterset.qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(form=self.filterset.form)
        return context


class BaseFilterList(FilterSetMixin, BaseList):
    def get_filterset_kwargs(self):
        kw = super().get_filterset_kwargs()
        kw.update(assessment=self.assessment)
        return kw


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


def htmx_required(func):
    """Require request to be have HX-Request header."""

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.headers.get("HX-Request", "") != "true":
            return HttpResponseBadRequest("An HTMX request is required")
        return func(request, *args, **kwargs)

    return wrapper


@dataclass
class FormsetConfiguration:
    """
    dataclass containing all the information needed to render one or more child formsets as part of another form.

    No functionality; just a convenient grouping of fields.
    """

    fragment: str  # path to the template fragment for this formset
    form_class: type  # class/type; subclass of django.forms.ModelForm
    model_class: type  # class/type; subclass of django.db.models.Model
    helper_class: type  # class/type; a django form helper
    sort_field: str  # field used to sort when retrieving items being displayed in the subformset
    form_prefix: str  # prefix passed to modelformset_factory during formset construction
