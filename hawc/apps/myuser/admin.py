from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..bmd.diagnostics import diagnostic_bmds2_execution
from ..common.diagnostics import (
    diagnostic_500,
    diagnostic_cache,
    diagnostic_celery_task,
    diagnostic_email,
)
from . import forms, models


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

    def save_model(self, request, obj, form, change):
        form.save(commit=True)

    set_password.short_description = "Set user-password"
    send_welcome_emails.short_description = "Send welcome email"

    actions = (
        send_welcome_emails,
        set_password,
        diagnostic_500,
        diagnostic_celery_task,
        diagnostic_cache,
        diagnostic_email,
        diagnostic_bmds2_execution,
    )
