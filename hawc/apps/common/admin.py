from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect, AutocompleteSelectMultiple
from django.urls import reverse
from django.utils.safestring import mark_safe


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


class ReadOnlyTabularInline(admin.TabularInline):
    def has_add_permission(self, request, obj):
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


def autocomplete(Model, field: str, multi: bool = False):
    """Build an autocomplete widget for the admin.

    Args:
        Model (django.models.Model): A django model class
        field (str): The field name
        multi (bool, optional): If true, a multiselect, defaults to a single select.
    """
    Widget = AutocompleteSelectMultiple if multi else AutocompleteSelect
    return Widget(Model._meta.get_field(field), admin.site, attrs={"style": "min-width: 600px"})


@admin.display(description="Detailed edit link")
def admin_edit_link(instance):
    """
    Generate a read-only edit link in the admin for detailed editing.
    """
    if instance.pk:
        url = reverse(
            f"admin:{instance._meta.app_label}_{instance._meta.model_name}_change",
            args=(instance.pk,),
        )
        return mark_safe(f'<a href="{url}">edit</a>')
    return mark_safe("<i>N/A - save current form first</i>")
