from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator


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


class ReadWriteSerializerMixin:
    """
    idea from https://www.revsys.com/tidbits/using-different-read-and-write-serializers-django-rest-framework/
    """

    read_serializer_class = None
    write_serializer_class = None

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return self.get_write_serializer_class()
        return self.get_read_serializer_class()

    def get_read_serializer_class(self):
        assert self.read_serializer_class is not None, (
            "'%s' should either include a `read_serializer_class` attribute,"
            "or override the `get_read_serializer_class()` method." % self.__class__.__name__
        )
        return self.read_serializer_class

    def get_write_serializer_class(self):
        assert self.write_serializer_class is not None, (
            "'%s' should either include a `write_serializer_class` attribute,"
            "or override the `get_write_serializer_class()` method." % self.__class__.__name__
        )
        return self.write_serializer_class


class GetOrCreateMixin:
    """
    this should be mixed into a serializer that has:
    1. a Meta class with a defined model (and a list_serializer_class
        referring to the GenericGetOrCreateListSerializer, if multiple
        support)
    2. a defined method "getOrCreatePermissionCheckHelper" that knows how to
        handle a single JSON representation of an object and check edit
        permissions for that object against a user, throwing an exception
        if permissions are lacking.

   This mixin:
    1. disables any UniqueTogetherValidators
    2. overrides create to actually call get_or_create
    3. for either single item or list item creation, calls the
       "getOrCreatePermissionCheckHelper" method for individual creation
       candidate elements.

    Use case - consider a model like epi.models.Criteria; this contains a
    unique_together meta restriction on the "assessment" and "description"
    fields. Or in other words, in the database assessment+description are
    guaranteed to be unique.

    We want to build an API able to support something like a POST
    { "assessment": 1, "description": "foo" }
    to the endpoint defined for this. A normal serializer will complain
    if a criteria with that description already exists, due to the
    UniqueTogetherValidator firing. If instead we mix this class into
    the appropriate serializer, we can code things such that the first call
    will create a criteria with description "foo", and the second
    call will just fetch the existing one. This makes client construction
    just a little more straightforward -- rather than having to
    lookup/check/create-if-needed, clients can just hit one endpoint and
    get back the object.

    What's more, we want to possibly support doing this mix of create and
    lookup for multiple criteria in a single API call. This mixin helps
    reduce duplicated code for both of these behaviors.

    Basic approach taken from https://stackoverflow.com/questions/25026034/django-rest-framework-modelserializer-get-or-create-functionality
   """

    class GenericGetOrCreateListSerializer(serializers.ListSerializer):
        def custom_perm_checker(self, user):
            for item in self.child.initial_data:
                self.child.getOrCreatePermissionCheckHelper(item, user)

    def custom_perm_checker(self, user):
        self.getOrCreatePermissionCheckHelper(self.initial_data, user)

    def run_validators(self, value):
        for validator in self.validators:
            if isinstance(validator, UniqueTogetherValidator):
                self.validators.remove(validator)
        super().run_validators(value)

    def create(self, validated_data, *args, **kwargs):
        instance, created = self.Meta.model.objects.get_or_create(**validated_data)
        return instance
