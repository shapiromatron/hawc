from dal import autocomplete
from django.core.exceptions import BadRequest, FieldError
from django.http import HttpResponseForbidden

from ..helper import reverse_with_query_lazy


class BaseAutocomplete(autocomplete.Select2QuerySetView):
    filter_fields: list[str] = []
    order_by: str = ""
    order_direction: str = ""
    paginate_by: int = 30

    def get_field(self, obj):
        return getattr(obj, self.field)

    def get_field_result(self, obj):
        return {
            "id": self.get_result_value(obj),
            "text": self.get_field(obj),
            "selected_text": self.get_field(obj),
        }

    def get_result(self, obj):
        return {
            "id": self.get_result_value(obj),
            "text": self.get_result_label(obj),
            "selected_text": self.get_selected_result_label(obj),
        }

    def get_results(self, context):
        return [
            self.get_field_result(obj) if self.field else self.get_result(obj)
            for obj in context["object_list"]
        ]

    def update_qs(self, qs):
        return qs

    @classmethod
    def get_base_queryset(cls, filters: dict | None = None):
        """
        Gets the base queryset to perform searches on

        Args:
            filters (dict, optional): Field/value pairings to filter queryset on, as long as fields are in class property filter_fields

        Returns:
            QuerySet: Base queryset
        """
        filters = filters or {}
        filters = {key: filters[key] for key in filters if key in cls.filter_fields}
        qs = cls.model.objects.all()
        return qs.filter(**filters)

    def _clean_query(self):
        self.qry = self.request.GET.dict()
        if "q" in self.qry:
            self.qry["q"] = self.qry["q"].replace("\0", "")
        self.q = self.q.replace("\0", "")

    def get_queryset(self):
        self._clean_query()
        # get base queryset
        try:
            qs = self.get_base_queryset(self.qry)
        except ValueError:
            raise BadRequest("Invalid filter parameters")

        # check forwarded values for search_fields
        self.search_fields = self.forwarded.get("search_fields") or self.search_fields

        # perform search
        qs = self.get_search_results(qs, self.q)

        if self.field:
            # order by field and get distinct
            try:
                qs = qs.order_by(self.field).distinct(self.field)
            except FieldError:
                raise BadRequest("Invalid field parameters")
        else:
            # check forwarded values for ordering
            self.order_by = self.forwarded.get("order_by") or self.order_by
            self.order_direction = self.forwarded.get("order_direction") or self.order_direction
            if self.order_by:
                qs = qs.order_by(self.order_direction + self.order_by)

        return qs

    def dispatch(self, request, *args, **kwargs):
        self.field = request.GET.get("field", "")
        if self.field:
            self.search_fields = [self.field]
        return super().dispatch(request, *args, **kwargs)

    @classmethod
    def registry_key(cls):
        app_name = cls.__module__.split(".")[-2].lower()
        class_name = cls.__name__.lower()
        return f"{app_name}-{class_name}"

    @classmethod
    def url(cls, **kwargs):
        # must lazily reverse url to prevent circular imports
        return reverse_with_query_lazy("autocomplete", args=[cls.registry_key()], query=kwargs)


class BaseAutocompleteAuthenticated(BaseAutocomplete):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        return super().dispatch(request, *args, **kwargs)


class SearchLabelMixin:
    """
    Constructs autocomplete labels by using values from the search_fields
    """

    def get_result_label(self, result):
        labels = []
        for path in self.search_fields:
            item = result
            for attribute in path.split("__"):
                item = getattr(item, attribute)
            labels.append(str(item))
        return " | ".join(labels)
