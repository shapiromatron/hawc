import warnings
from urllib.parse import urljoin

from rest_framework.schemas.openapi import SchemaGenerator


class CompleteSchemaGenerator(SchemaGenerator):
    """
    Remove permission checking during endpoint determination.

    Subclass of rest_framework.schemas.openapi.SchemaGenerator; this view for
    the admin should allow for all endpoints. The current approach fails because
    of the implementation of hawc.apps.assessment.api.AssessmentLevelPermissions where
    in list views the `assessment_id` query parameter is required.
    """

    def get_schema(self, request=None, public=False):
        """
        Generate a OpenAPI schema.
        """
        self._initialise_endpoints()
        components_schemas = {}

        # Iterate endpoints generating per method path operations.
        paths = {}
        _, view_endpoints = self._get_paths_and_endpoints(None if public else request)
        for path, method, view in view_endpoints:
            # ------------------------------------ PATCH START ------------------------------------
            # https://github.com/encode/django-rest-framework/blob/efc7c1d664e5909f5f1f4d07a7bb70daef1c396e/rest_framework/schemas/openapi.py#L78-L79
            # if not self.has_view_permissions(path, method, view):
            #    continue
            # ------------------------------------ PATCH END   ------------------------------------

            operation = view.schema.get_operation(path, method)
            components = view.schema.get_components(path, method)
            for k in components.keys():
                if k not in components_schemas:
                    continue
                if components_schemas[k] == components[k]:
                    continue
                warnings.warn(
                    f'Schema component "{k}" has been overridden with a different value.',
                    stacklevel=1,
                )

            components_schemas.update(components)

            # Normalise path for any provided mount url.
            if path.startswith("/"):
                path = path[1:]
            path = urljoin(self.url or "/", path)

            paths.setdefault(path, {})
            paths[path][method.lower()] = operation

        self.check_duplicate_operation_id(paths)

        # Compile final schema.
        schema = {
            "openapi": "3.0.2",
            "info": self.get_info(),
            "paths": paths,
        }

        if len(components_schemas) > 0:
            schema["components"] = {"schemas": components_schemas}

        return schema
