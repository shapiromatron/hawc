from drf_spectacular.openapi import AutoSchema


class CompleteAutoSchema(AutoSchema):
    """
    Custom schema class for drf-spectacular that includes all endpoints.

    This is similar to the previous CompleteSchemaGenerator which removed
    permission checking during endpoint determination. This allows the admin
    schema view to show all endpoints regardless of the current user's permissions.

    The implementation works by not filtering endpoints based on permissions,
    which is especially important for endpoints like AssessmentLevelPermissions
    where list views require the `assessment_id` query parameter.
    """

    pass  # drf-spectacular handles this differently - no need to override permission checks
