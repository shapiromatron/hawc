from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.response import Response


class ListUpdateModelMixin:
    """
    Taken from https://github.com/chibisov/drf-extensions
    and isolated for Django 3.1 compatibility;
    https://github.com/chibisov/drf-extensions/commit/8001a440c7322be26bbe2d16f3a334a8b0b5860b
    fix not on an official release yet
    """

    def __init__(self, *args, **kwargs):
        _settings = getattr(settings, "REST_FRAMEWORK_EXTENSIONS", {})
        self.bulk_header = _settings.get("DEFAULT_BULK_OPERATION_HEADER_NAME", "X-BULK-OPERATION")
        super().__init__(*args, **kwargs)

    def is_object_operation(self):
        return bool(self.get_object_lookup_value())

    def get_object_lookup_value(self):
        return self.kwargs.get(getattr(self, "lookup_url_kwarg", None) or self.lookup_field, None)

    def is_valid_bulk_operation(self):
        if self.bulk_header:
            header_name = "http_{0}".format(self.bulk_header.strip().replace("-", "_")).upper()
            return (
                bool(self.request.META.get(header_name, None)),
                {
                    "detail": "Header '{0}' should be provided for bulk operation.".format(
                        self.bulk_header
                    )
                },
            )
        else:
            return True, {}

    def patch(self, request, *args, **kwargs):
        if self.is_object_operation():
            return super().partial_update(request, *args, **kwargs)
        else:
            return self.partial_update_bulk(request, *args, **kwargs)

    def partial_update_bulk(self, request, *args, **kwargs):
        is_valid, errors = self.is_valid_bulk_operation()
        if is_valid:
            queryset = self.filter_queryset(self.get_queryset())
            update_bulk_dict = self.get_update_bulk_dict(
                serializer=self.get_serializer_class()(), data=request.data
            )
            self.pre_save_bulk(queryset, update_bulk_dict)
            try:
                queryset.update(**update_bulk_dict)
            except ValueError as e:
                errors = {"detail": force_str(e)}
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            self.post_save_bulk(queryset, update_bulk_dict)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def get_update_bulk_dict(self, serializer, data):
        update_bulk_dict = {}
        for field_name, field in serializer.fields.items():
            if field_name in data and not field.read_only:
                update_bulk_dict[field.source or field_name] = data[field_name]
        return update_bulk_dict

    def pre_save_bulk(self, queryset, update_bulk_dict):
        pass

    def post_save_bulk(self, queryset, update_bulk_dict):
        pass


class DynamicFieldsMixin:
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    Usage::
        class MySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
            class Meta:
                model = MyModel
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("request"):
            fields = self.context.get("request").query_params.get("fields")
            if fields:
                fields = fields.split(",")
                # Drop fields that are not specified in the `fields` argument.
                fields.extend(["id", "name"])
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)


class LegacyAssessmentAdapterMixin:
    """
    A mixin that allows API viewsets to interact with legacy methods.
    """

    def set_legacy_attr(self, pk):
        self.parent = get_object_or_404(self.parent_model, pk=pk)
        self.assessment = self.parent.get_assessment()
