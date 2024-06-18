from django.contrib import admin
from reversion.models import Revision, Version

from ..common.admin import ReadOnlyAdmin, ReadOnlyTabularInline


class VersionInline(ReadOnlyTabularInline):
    model = Version


@admin.register(Revision)
class RevisionAdmin(ReadOnlyAdmin):
    list_display = ("id", "date_created", "user", "comment")
    list_filter = ("date_created", "user")
    list_select_related = ("user",)
    inlines = (VersionInline,)


@admin.register(Version)
class VersionAdmin(ReadOnlyAdmin):
    list_display = ("id", "object_id", "content_type", "get_created_date")
    list_filter = ("content_type",)

    @admin.display(description="Created", ordering="revision__date_created")
    def get_created_date(self, obj):
        return obj.revision.date_created

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("content_type", "revision")
