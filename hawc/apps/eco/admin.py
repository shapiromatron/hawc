from django.contrib import admin

from ..common.admin import admin_edit_link
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
    list_display = ("id", "__str__", "study", "design", "created", "last_updated")
    list_filter = ("design", "habitat")
    search_fields = ("study__short_citation",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study", "design")


class EffectTabularAdmin(admin.StackedInline):
    model = models.Effect
    form = forms.EffectForm
    extra = 0
    readonly_fields = (admin_edit_link,)


@admin.register(models.Cause)
class CauseAdmin(admin.ModelAdmin):
    form = forms.CauseForm
    list_display = ("id", "__str__", "study", "created", "last_updated")
    search_fields = ("study__short_citation",)
    inlines = [EffectTabularAdmin]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study", "term")


class QuantitativeInlineAdmin(admin.TabularInline):
    model = models.Quantitative
    extra = 0
    readonly_fields = (admin_edit_link,)

    @admin.display(description="Detailed edit link")
    def edit_link(self, instance):
        return admin_edit_link(instance)


@admin.register(models.Effect)
class EffectAdmin(admin.ModelAdmin):
    form = forms.EffectForm
    list_display = ("id", "cause", "term", "created", "last_updated")
    search_fields = ("cause__study__short_citation",)
    inlines = [QuantitativeInlineAdmin]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("cause__study", "term")


@admin.register(models.Quantitative)
class QuantitativeAdmin(admin.ModelAdmin):
    model = models.Quantitative
    form = forms.QuantitativeForm
    list_display = (
        "id",
        "effect",
        "sort_order",
        "created",
        "last_updated",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("effect__cause__study")
