from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from . import models


class HAWCUserAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'email', 'is_active',
                    'is_staff', 'date_joined')
    list_filter = ('date_joined', )
    search_fields = ('last_name', 'first_name', 'email')
    ordering = ('-date_joined', )

    def send_welcome_emails(modeladmin, request, queryset):
        for user in queryset:
            user.send_welcome_email()

        modeladmin.message_user(request, "Welcome email(s) sent!")

    def set_password(modeladmin, request, queryset):
        if queryset.count() != 1:
            return modeladmin.message_user(
                request,
                "Please select only-one user",
                level=messages.ERROR)

        return HttpResponseRedirect(
            reverse('user:set_password', kwargs={'pk': queryset.first().id}))


    set_password.short_description = "Set user-password"
    send_welcome_emails.short_description = "Send welcome email"

    actions = (send_welcome_emails, set_password)


admin.site.register(models.HAWCUser, HAWCUserAdmin)
