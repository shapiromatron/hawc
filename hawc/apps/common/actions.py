import json
from collections import defaultdict
from typing import Any, ClassVar

import pandas as pd
import pydantic
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

DataModel = type[pydantic.BaseModel]


class BaseApiAction:
    """
    An API action that's not tied to a database model schema. Mapping to a drf serializer is not
    ideal, so instead we bind to a pydantic data model.

    The main entrypoint is `ApiActionRequest.handle_request`; which takes a request and returns
    a response; however a standard class initialization can be used with data in the form of a
    python dictionary.
    """

    input_model: ClassVar[DataModel]  # should be defined

    def __init__(self, data: dict | None = None):
        self.data: dict = data or {}
        self.errors: dict[str, list] = defaultdict(list)
        self.inputs = None

    @classmethod
    def format_request_data(cls, request: Request) -> dict:
        """Convert a request into a dictionary of data for the action request

        Args:
            request (Request): The incoming request

        Returns:
            dict: A valid dictionary ready for the action
        """
        return request.data

    @classmethod
    def handle_request(cls, request: Request, atomic: bool = False) -> Response:
        """Handle the API request and response; throws standard django rest framework lifecycle
        errors if the response is invalid.

        Args:
            request (Request): The incoming request
            atomic (bool, optional): Should `execute` be wrapped in a transaction. Defaults to False.

        Raises:
            drf.ValidationError: If request data is invalid
            drf.PermissionDenied: If permission is denied

        Returns:
            Response: A drf.Response
        """
        instance = cls(data=cls.format_request_data(request))

        instance.validate(raise_exception=True)

        # check permissions
        has_permission, reason = instance.has_permission(request)
        if not has_permission:
            raise PermissionDenied(reason)

        # perform action
        if atomic:
            with transaction.atomic():
                response = instance.evaluate()
        else:
            response = instance.evaluate()

        # return response
        return Response(response)

    def validate(self, raise_exception: bool = False):
        # parse primitive data types
        try:
            self.inputs = self.input_model.model_validate(self.data)
        except pydantic.ValidationError as err:
            self.errors = json.loads(err.json())

        # validate business logic
        if len(self.errors) == 0:
            self.validate_business_logic()

        if raise_exception and self.errors:
            raise ValidationError(self.errors)

    @property
    def is_valid(self):
        return self.inputs is not None and len(self.errors) == 0

    def validate_business_logic(self):
        """Validate input data beyond the primitive data types.

        This method also frequently sets additional class attributes.

        An example check:

        if self.inputs.swallow == "brazil":
            self.errors["swallow"].append("Only african or european are allowed")
        """
        pass

    def has_permission(self, request: Request) -> tuple[bool, str]:
        """Any additional permission checks after business logic has been validated.

        Returns:
            tuple[bool, str]: has_permission, reason (if permission denied)
        """
        return True, ""

    def evaluate(self) -> dict[str, Any] | pd.DataFrame:
        """
        Perform the desired action of the request action. Returns a response type compatible
        with the desired action
        """
        return {}
