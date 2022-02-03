import warnings
from urllib.parse import urljoin

from rest_framework.schemas.openapi import SchemaGenerator


class OpenAPIGenerator(SchemaGenerator):
    """
    This subclass removes permission checks during endpoint determination, since we want all
    endpoints to be shown and some permission checks will fail without additional query params
    (AssessmentLevelPermissions)
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

            """
            Permission checks are removed here:

            if not self.has_view_permissions(path, method, view):
                continue
            """

            operation = view.schema.get_operation(path, method)
            components = view.schema.get_components(path, method)
            for k in components.keys():
                if k not in components_schemas:
                    continue
                if components_schemas[k] == components[k]:
                    continue
                warnings.warn(
                    'Schema component "{}" has been overriden with a different value.'.format(k)
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
