from django.contrib import admin

from . import forms, models


@admin.register(models.State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("name",)


@admin.register(models.Vocab)
class VocabAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "value", "parent")
    list_filter = ("category",)
    search_fields = ("value",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("parent")


@admin.register(models.Metadata)
class MetadataAdmin(admin.ModelAdmin):
    form = forms.MetadataForm
    list_display = (
        "id",
        "__str__",
        "study",
    )
    list_filter = ("habitat",)
    search_fields = ("study__short_citation",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study")


@admin.register(models.Cause)
class CauseAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Effect)
class EffectAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Quantitative)
class QuantitativeAdmin(admin.ModelAdmin):
    pass
