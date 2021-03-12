from .tasks import bmds2_service_healthcheck


def diagnostic_bmds2_execution(modeladmin, request, queryset):
    result = bmds2_service_healthcheck.delay()
    success = result.get(60)
    if success:
        message = "BMDS2 remote execution completed successfully."
    else:
        message = "BMDS2 did not return successfully."
    modeladmin.message_user(request, message)


diagnostic_bmds2_execution.short_description = "Diagnostic BMDS2 run"
