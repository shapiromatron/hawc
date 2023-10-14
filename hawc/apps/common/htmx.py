from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import wraps
from typing import Any

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
)
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic import View

from ..assessment.models import Assessment
from ..assessment.permissions import AssessmentPermissions
from .exceptions import AssessmentNotFound
from .views import create_object_log


@dataclass
class Item:
    """
    Object, related assessment, and permissions for an item in an view request.
    """

    assessment: Assessment
    object: Any | None
    parent: Any | None

    def __post_init__(self):
        self.assessment_permissions: AssessmentPermissions = self.assessment.get_permissions()
        self._permissions: dict[str, bool] | None = None

    def to_dict(self, user) -> dict[str, Any]:
        """Dictionary used for response context"""
        return {
            "assessment": self.assessment,
            "object": self.object,
            "parent": self.parent,
            "permissions": self.permissions(user),
        }

    def permissions(self, user) -> dict:
        """Generate user specific permissions for this request; cached"""
        if self._permissions is None:
            perms_item = self.parent or self.object  # use parent if exists, else object
            study = perms_item.get_study() if hasattr(perms_item, "get_study") else None
            self._permissions = self.assessment_permissions.to_dict(user, study)
        return self._permissions


def is_htmx(request) -> bool:
    """Was this request initiated by HTMX?"""
    return request.headers.get("HX-Request", "") == "true"


# Permissions function checks for @action decorator
def allow_any(user, item: Item | None) -> bool:
    """Allow any request"""
    return True


def deny_all(user, item: Item | None) -> bool:
    """Deny all requests"""
    return False


def staff_only(user, item: Item | None) -> bool:
    """Staff only requests"""
    return user.is_staff


def can_view(user, item: Item | None) -> bool:
    """Can a user view this hawc item? Equivalent to a reviewer on non-public assessments"""
    return item.permissions(user)["view"] if item else False


def can_edit(user, item: Item | None) -> bool:
    """Can a user edit this item? Equivalent to assessment team-member or higher"""
    return item.permissions(user)["edit"] if item else False


def can_edit_assessment(user, item: Item | None) -> bool:
    """Can a user edit this item? Equivalent to project-manager or higher"""
    return item.permissions(user)["edit_assessment"] if item else False


def action(
    permission: Callable = deny_all, htmx_only: bool = True, methods: Iterable[str] = ("get",)
):
    """Decorator for an HtmxViewSet action method

    Influenced by django-rest framework's ViewSet action decorator; permissions checking that
    the user making the request can make this request, and the request is valid.

    Args:
        permission (Callable, optional, default deny all): A permission function; returns True/False
        htmx_only (bool, optional, default True): Accept only htmx requests
        methods (Iterable[str]): Accepted http methods; defaults to ("get",)
    """

    def actual_decorator(func):
        @wraps(func)
        def wrapper(view, request, *args, **kwargs):
            # check if htmx is required
            if htmx_only and not is_htmx(request):
                return HttpResponseBadRequest("An HTMX request is required")
            # check valid view method
            if request.method.lower() not in methods:
                return HttpResponseNotAllowed("Invalid HTTP method")
            # check permissions
            if not permission(request.user, getattr(request, "item", None)):
                raise PermissionDenied()
            return func(view, request, *args, **kwargs)

        return wrapper

    return actual_decorator


class HtmxViewSet(View):
    """
    Base class for implementing htmx-based actions for a given model resource.

    Attributes:
        actions: set[str]; individual URL-routes for each action on a view. You can add or remove
            items from this list; each action requires a URL route, and a method added to this
            ViewSet for handling logic.
        parent_actions: set[str]; any actions which require a parent object, not the object
            itself. This is commonly done for create and list views since the object does not
            yet exist or there may be multiple objects.
        pk_url_kwarg: str; the name of the item in the URL (from standard django class-based views)
        parent_model: A Django models.Model for parent class
        model: A Django models.Model for the base class
    """

    actions: set[str] = {"create", "read", "update", "delete", "list"}
    parent_actions: set[str] = {"create", "list"}
    pk_url_kwarg: str = "pk"
    parent_model: Any = None
    model: Any = None

    def get_item(self, request: HttpRequest) -> Item:
        object = None
        parent = None
        if request.action in self.parent_actions:
            parent = get_object_or_404(self.parent_model, pk=self.kwargs.get(self.pk_url_kwarg))
        else:
            object = get_object_or_404(self.model, pk=self.kwargs.get(self.pk_url_kwarg))
        try:
            assessment: Assessment = parent.get_assessment() if parent else object.get_assessment()
        except AssessmentNotFound:
            raise PermissionDenied()
        return Item(object=object, parent=parent, assessment=assessment)

    def get_context_data(self, **kwargs):
        context = self.request.item.to_dict(self.request.user)
        context.update(action=self.request.action, **kwargs)
        return context

    def dispatch(self, request, *args, **kwargs):
        request.is_htmx = is_htmx(request)
        request.action = self.kwargs.get("action", "<none>").lower()
        if request.action not in self.actions:
            return HttpResponseNotFound()
        handler = getattr(self, request.action, self.http_method_not_allowed)
        request.item = self.get_item(request)
        return handler(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, item: Item, form):
        item.object = form.save()
        create_object_log("Created", item.object, item.assessment.id, self.request.user.id)

    @transaction.atomic
    def perform_update(self, item: Item, form):
        instance = form.save()
        create_object_log("Updated", instance, item.assessment.id, self.request.user.id)

    @transaction.atomic
    def perform_delete(self, item: Item):
        create_object_log("Deleted", item.object, item.assessment.id, self.request.user.id)
        item.object.delete()

    @transaction.atomic
    def perform_clone(self, item: Item):
        item.object.clone()
        create_object_log("Created", item.object, item.assessment.id, self.request.user.id)

    def str_response(self, text: str = "") -> HttpResponse:
        """Return a string-based response; by default an empty string"""
        return HttpResponse(text)


class HtmxView(View):
    """Build a generic HtmxView which returns a index full page and multiple fragments.

    If a valid "action" is specified via a GET parameter, a partial is returned, otherwise
    the default_action ("index") is returned. It is generally assumed that the default_action
    is a full page, while all other pages are fragments.
    """

    actions: set[str]
    default_action: str = "index"

    def get_handler(self, request: HttpRequest):
        request.action = request.GET.get("action", "")
        if request.action not in self.actions:
            request.action = self.default_action
        return getattr(self, request.action, self.http_method_not_allowed)

    def dispatch(self, request, *args, **kwargs):
        handler = self.get_handler(request)
        return handler(request, *args, **kwargs)


class HtmxGetMixin:
    """Returns a either a full template or partial based on GET parameter in request.

    If a valid "action" is specified via a GET parameter, a partial is returned, otherwise
    the default_action ("index") is returned. It is generally assumed that the default_action
    is a full page, while all other pages are fragments.

    The default context is provided for all actions.
    """

    actions: set[str]
    default_action: str = "index"

    def get_handler(self, request: HttpRequest):
        request.action = request.GET.get("action", "")
        if request.action not in self.actions:
            request.action = self.default_action
        return getattr(self, request.action, self.http_method_not_allowed)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        handler = self.get_handler(request)
        return handler(request, context)
