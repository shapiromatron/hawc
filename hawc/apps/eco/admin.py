from django.contrib import admin
from treebeard.admin import TreeAdmin

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


@admin.register(models.Design)
class DesignAdmin(admin.ModelAdmin):
    form = forms.DesignForm
    list_display = ("id", "__str__", "study", "design", "created", "last_updated")
    list_filter = ("design", "habitats")
    search_fields = ("study__short_citation",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study", "design")


@admin.register(models.Cause)
class CauseAdmin(admin.ModelAdmin):
    form = forms.CauseForm
    list_display = ("id", "__str__", "study", "created", "last_updated")
    list_filter = (("study", admin.RelatedOnlyFieldListFilter),)
    search_fields = ("study__short_citation",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study", "term")


class ResultInlineAdmin(admin.TabularInline):
    model = models.Result
    extra = 0
    readonly_fields = (admin_edit_link,)

    @admin.display(description="Detailed edit link")
    def edit_link(self, instance):
        return admin_edit_link(instance)


@admin.register(models.Effect)
class EffectAdmin(admin.ModelAdmin):
    form = forms.EffectForm
    list_display = ("id", "study", "term", "created", "last_updated")
    search_fields = ("study__short_citation",)
    inlines = [ResultInlineAdmin]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study", "term")


@admin.register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    model = models.Result
    form = forms.ResultForm
    list_display = (
        "id",
        "design",
        "cause",
        "effect",
        "sort_order",
        "created",
        "last_updated",
    )
    list_filter = (
        ("design", admin.RelatedOnlyFieldListFilter),
        ("cause", admin.RelatedOnlyFieldListFilter),
        ("effect", admin.RelatedOnlyFieldListFilter),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("design", "cause", "effect")


@admin.register(models.NestedTerm)
class NestedTermAdmin(TreeAdmin):
    pass
