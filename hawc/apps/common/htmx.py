from dataclasses import asdict, dataclass
from functools import wraps
from typing import Any, Callable, Iterable, Optional, Set

from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic import View

from ..assessment.models import Assessment
from ..assessment.permissions import AssessmentPermissions


@dataclass
class Item:
    assessment: Assessment
    object: Any  # item or parent model instance
    objects: Optional[QuerySet] = None  # items in a list view

    def __post_init__(self):
        self.permissions: AssessmentPermissions = self.assessment.get_permissions()

    def to_dict(self):
        return asdict(self)


def is_htmx(request) -> bool:
    return request.headers.get("HX-Request", "") == "true"


def can_view_study_items(user, item: Item) -> bool:
    # TODO - fix
    return True


def can_edit_study_item(user, item: Item) -> bool:
    # TODO - fix
    return True


# influenced by:
# https://github.com/encode/django-rest-framework/blob/master/rest_framework/decorators.py
def action(permission: Callable, htmx: bool = False, methods: Optional[Iterable[str]] = None):
    """Action handler for our custom htmx-based viewset

    Args:
        permission (Callable): A permssion function that returns True/False
        htmx (bool, optional, default False): Only accepts htmx requests
        methods (Optional[Iterable[str]]): Accepted http methods; defaults to {"get"} if undefined.

    Raises:
        PermissionDenied: [description]

    Returns:
        [type]: [description]
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


# http://127.0.0.1:8000/ani/v2/experiment/study/3297/create/

# todo - add a decorator for permissions class - assessment_perms, study_perms
# todo - override template renderer to check if permission_checked = True; set to false at beginning
# todo - pass in study to item for some checks
# todo rename object to parent_object in some cases


class CrudModelViewSet(View):
    actions: Set[str] = {"create", "read", "update", "delete", "list"}
    parent_actions: Set[str] = {"create", "list"}
    list_actions: Set[str] = {"list"}
    pk_url_kwarg: str = "pk"
    parent_model: Any = None
    model: Any = None

    def get_item(self, request: HttpRequest) -> Item:
        Model = self.parent_model if request.from_parent_id else self.model
        object = get_object_or_404(Model, pk=self.kwargs.get(self.pk_url_kwarg))
        assessment: Assessment = object.get_assessment()
        item = Item(object=object, assessment=assessment)
        if request.action in self.list_actions:
            item.objects = self.get_objects(item)
        return item

    def get_objects(self, item: Item) -> QuerySet:
        raise NotImplementedError("Requires custom implementation.")

    def dispatch(self, request, *args, **kwargs):
        request.is_htmx = request.headers.get("HX-Request", "false").lower() == "true"
        request.action = self.kwargs.get("action", "<none>").lower()
        request.from_parent_id = request.action in self.parent_actions
        if request.action in self.actions:
            handler = getattr(self, request.action, self.http_method_not_allowed)
        else:
            return HttpResponseNotFound()
        request.item = self.get_item(request)
        return handler(request, *args, **kwargs)
