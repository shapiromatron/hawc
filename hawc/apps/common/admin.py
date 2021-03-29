from django.contrib import admin


class AllListFieldAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class YesNoFilter(admin.SimpleListFilter):
    """
    Filter to include/exclude a query.
    Inclusion is displayed as "Yes" and exclusion by "No"

    Attributes:
        title: Display name of the filter ("Filter by <title>")
        parameter_name: URL parameter name for the query
        query: A Q object used as the inclusion condition
    """

    query = None

    def __init__(self, request, params, model, model_admin):
        if self.query is None:
            raise AttributeError("Class attribute 'query' must be set.")
        super().__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        return (
            ("Yes", "Yes"),
            ("No", "No"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.filter(self.query)
        elif value == "No":
            return queryset.exclude(self.query)
        return queryset
