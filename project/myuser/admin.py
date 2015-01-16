from django.contrib import admin

from . import models


def send_welcome_emails(modeladmin, request, queryset):
    for user in queryset:
        user.send_welcome_email()

    modeladmin.message_user(request, "Welcome email(s) sent!")

send_welcome_emails.short_description = "Send welcome email"

class HAWCUserAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'email', 'is_active',  'is_staff', 'date_joined')
    list_filter = ('date_joined', )
    search_fields = ('last_name', 'first_name', 'email')
    ordering = ('-date_joined', )

    actions = [send_welcome_emails]


admin.site.register(models.HAWCUser, HAWCUserAdmin)
