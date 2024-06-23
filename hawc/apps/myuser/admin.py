from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from ...constants import AuthProvider
from ..common.diagnostics import (
    clear_cache,
    diagnostic_500,
    diagnostic_cache,
    diagnostic_celery_task,
    diagnostic_email,
)
from . import forms, models


class UserProfileAdmin(admin.StackedInline):
    model = models.UserProfile


@admin.register(models.HAWCUser)
class HAWCUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "external_id",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "last_login",
        "date_joined",
        "email_verified_on",
    )
    list_filter = (
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
        "last_login",
        "email_verified_on",
        "groups",
    )
    search_fields = ("last_name", "first_name", "email", "external_id")
    ordering = ("-date_joined",)
    form = forms.AdminUserForm
    inlines = [UserProfileAdmin]

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Send welcome email")
    def send_welcome_emails(modeladmin, request, queryset):
        for user in queryset:
            user.send_welcome_email()

        modeladmin.message_user(request, "Welcome email(s) sent!")

    @admin.action(description="Send email verification email")
    def send_email_verification_email(modeladmin, request, queryset):
        for user in queryset:
            user.send_email_verification(request)
        modeladmin.message_user(request, "Email verification email(s) sent!")

    @admin.action(description="Set user-password")
    def set_password(modeladmin, request, queryset):
        if settings.AUTH_PROVIDERS == {AuthProvider.external}:
            return modeladmin.message_user(
                request, "Password cannot be set when using external auth", level=messages.ERROR
            )
        if queryset.count() != 1:
            return modeladmin.message_user(
                request, "Please select only-one user", level=messages.ERROR
            )

        return HttpResponseRedirect(
            reverse("user:set_password", kwargs={"pk": queryset.first().id})
        )

    def save_model(self, request, obj, form, change):
        form.save(commit=True)

    actions = (
        send_welcome_emails,
        send_email_verification_email,
        set_password,
        clear_cache,
        diagnostic_500,
        diagnostic_celery_task,
        diagnostic_cache,
        diagnostic_email,
    )
