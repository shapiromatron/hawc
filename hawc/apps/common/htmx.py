from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Iterable, Optional, Set

from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.http import (
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
    HttpResponse,
)
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic import View

from ..assessment.models import Assessment
from ..assessment.permissions import AssessmentPermissions
from .views import create_object_log


@dataclass
class Item:
    assessment: Assessment
    object: Optional[Any]
    parent: Optional[Any]

    def __post_init__(self):
        self.permissions: AssessmentPermissions = self.assessment.get_permissions()

    def to_dict(self, user):
        perms_item = self.parent if self.parent else self.object
        study = perms_item.get_study() if hasattr(perms_item, "get_study") else None
        return {
            "assessment": self.assessment,
            "object": self.object,
            "parent": self.parent,
            "permissions": self.permissions.to_dict(user, study),
        }


def is_htmx(request) -> bool:
    return request.headers.get("HX-Request", "") == "true"


def can_view(user, item: Item) -> bool:
    # todo - prevent duplication here and in context - add user?
    # http://127.0.0.1:8000/ani/v2/experiment/study/3297/
    return item.permissions.can_view_study(item.object.get_study(), user)


def can_edit(user, item: Item) -> bool:
    return item.permissions.can_edit_study(item.object.get_study(), user)


def action(permission: Callable, htmx: bool = True, methods: Optional[Iterable[str]] = None):
    """Action handler for an htmx-based viewset

    Influenced by django-rest framework's action decorator on viewsets.

    Args:
        permission (Callable): A permssion function that returns True/False
        htmx (bool, optional, default True): Accept only htmx requests
        methods (Optional[Iterable[str]]): Accepted http methods; defaults to {"get"} if undefined.
    """
    if methods is None:
        methods = {"get"}

    def actual_decorator(func):
        @wraps(func)
        def wrapper(view, request, *args, **kwargs):
            # check if htmx is required
            if htmx and not is_htmx(request):
                return HttpResponseBadRequest("HTMX request is required")
            # check valid view method
            if request.method.lower() not in methods:
                return HttpResponseNotAllowed(f"Allowed methods: {', '.join(methods)}")
            # check permissions
            if not permission(request.user, request.item):
                raise PermissionDenied()
            return func(view, request, *args, **kwargs)

        return wrapper

    return actual_decorator


class HtmxViewSet(View):
    actions: Set[str] = {"create", "read", "update", "delete", "list"}
    parent_actions: Set[str] = {"create", "list"}
    pk_url_kwarg: str = "pk"
    parent_model: Any = None
    model: Any = None

    def get_item(self, request: HttpRequest) -> Item:
        Model = self.parent_model if request.from_parent_id else self.model
        object = get_object_or_404(Model, pk=self.kwargs.get(self.pk_url_kwarg))
        assessment: Assessment = object.get_assessment()
        item = Item(object=object, assessment=assessment)
        return item

    def get_context_data(self, **kwargs):
        context = self.request.item.to_dict(self.request.user)
        context.update(action=self.request.action, **kwargs)
        return context

    def dispatch(self, request, *args, **kwargs):
        request.is_htmx = is_htmx(request)
        request.action = self.kwargs.get("action", "<none>").lower()
        request.from_parent_id = request.action in self.parent_actions
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

    def empty_response(self) -> HttpResponse:
        return HttpResponse("")
