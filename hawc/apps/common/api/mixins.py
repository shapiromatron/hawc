from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from .permissions import user_can_edit_object


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

    mixin that enforces specification of separate read & write serializers, for use
    in a viewset.
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
    this should be mixed into a serializer

   This mixin:
    1. disables any UniqueTogetherValidators
    2. overrides create to actually call get_or_create

    The end result is a serializer mixing this in can either lookup or create
    an element, so that clients can pass the same payload multiple times and get back
    consistent results (idempotency, more or less).

    To elaborate, as a use case consider a model like epi.models.Criteria;
    this contains a unique_together meta restriction on the "assessment"
    and "description" fields. Or in other words, in the database
    assessment+description are guaranteed to be unique.

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
    get back the same object id every time.

    Basic approach taken from https://stackoverflow.com/questions/25026034/django-rest-framework-modelserializer-get-or-create-functionality
   """

    def run_validators(self, value):
        for validator in self.validators:
            if isinstance(validator, UniqueTogetherValidator):
                self.validators.remove(validator)
        super().run_validators(value)

    def create(self, validated_data, *args, **kwargs):
        instance, created = self.Meta.model.objects.get_or_create(**validated_data)
        return instance


class PermCheckerMixin:
    """
    class to be mixed into api viewsets. Provides default "user_can_edit_object" checks during
    requests to create/update/destroy via API. Classes mixing this in should define a variable perm_checker_key
    which can be either a string or a list of strings that should be used as the source for the checks, via
    looking them up in the validated_data of the serializer.
    """

    def generate_things_to_check(self, serializer, append_self_obj):
        things_to_check = []

        # perm_checker_key can either be a string or an array of strings
        checker_keys = self.perm_checker_key
        if type(self.perm_checker_key) is str:
            checker_keys = [self.perm_checker_key]

        for checker_key in checker_keys:
            if checker_key in serializer.validated_data:
                things_to_check.append(serializer.validated_data.get(checker_key))

        if append_self_obj:
            things_to_check.append(self.get_object())

        return things_to_check

    def perform_create(self, serializer):
        for thing_to_check in self.generate_things_to_check(serializer, False):
            user_can_edit_object(
                thing_to_check, self.request.user, raise_exception=True,
            )
        super().perform_create(serializer)

    def perform_update(self, serializer):
        for thing_to_check in self.generate_things_to_check(serializer, True):
            user_can_edit_object(
                thing_to_check, self.request.user, raise_exception=True,
            )

        super().perform_update(serializer)

    def perform_destroy(self, instance):
        user_can_edit_object(
            instance, self.request.user, raise_exception=True,
        )
        super().perform_destroy(instance)


class FormIntegrationMixin:
    """
    mixin to be used with serializers. The serializer must define a "form_integration_class"
    and this mixin will then instantiate it with the data being passed to validate and
    see if the form returns is_valid() == True. If not, it raises a ValidationError.

    The serializer can optionally define a method "get_form_integration_kwargs" to pass
    additional custom kwargs to the form constructor.
    """

    def validate(self, data):
        # if we need it, self.instance is None on create and set to something on update...
        data = super().validate(data)

        custom_kwargs = {}
        custom_kwargs_op = getattr(self, "get_form_integration_kwargs", None)
        if callable(custom_kwargs_op):
            custom_kwargs = custom_kwargs_op(data)

        form = self.form_integration_class(data=data, **custom_kwargs)

        if form.is_valid() is False:
            raise serializers.ValidationError(form.errors)

        return data
