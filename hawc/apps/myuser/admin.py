from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from . import forms, models, tasks


class IntentionalException(Exception):
    """
    An intentionally thrown exception, used for testing in various deployment environments.
    """

    pass


@admin.register(models.HAWCUser)
class HAWCUserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "date_joined")
    list_filter = (
        "is_superuser",
        "is_staff",
        "date_joined",
        "groups",
    )
    search_fields = ("last_name", "first_name", "email")
    ordering = ("-date_joined",)
    form = forms.AdminUserForm

    def send_welcome_emails(modeladmin, request, queryset):
        for user in queryset:
            user.send_welcome_email()

        modeladmin.message_user(request, "Welcome email(s) sent!")

    def set_password(modeladmin, request, queryset):
        if queryset.count() != 1:
            return modeladmin.message_user(
                request, "Please select only-one user", level=messages.ERROR
            )

        return HttpResponseRedirect(
            reverse("user:set_password", kwargs={"pk": queryset.first().id})
        )

    def throw_500(modeladmin, request, queryset):
        message = f"User {request.user} intentionally threw a server error from the admin site."
        raise IntentionalException(message)

    def diagnostic_celery_task(modeladmin, request, queryset):
        response = tasks.diagnostic_celery_task.delay(request.user.id).get()
        message = f"Celery task executed successfully: {response}"
        modeladmin.message_user(request, message)

    def save_model(self, request, obj, form, change):
        form.save(commit=True)

    set_password.short_description = "Set user-password"
    send_welcome_emails.short_description = "Send welcome email"
    throw_500.short_description = "Intentionally throw a server error (500)"
    diagnostic_celery_task.short_description = "Run a diagnostic celery task"

    actions = (send_welcome_emails, set_password, throw_500, diagnostic_celery_task)
