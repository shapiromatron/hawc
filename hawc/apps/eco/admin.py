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


@admin.register(models.Design)
class DesignAdmin(admin.ModelAdmin):
    form = forms.DesignForm
    list_display = ("id", "__str__", "study", "design", "created", "last_updated")
    list_filter = ("design", "habitat")
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


@admin.register(models.Effect)
class EffectAdmin(admin.ModelAdmin):
    form = forms.EffectForm
    list_display = ("id", "study", "term", "created", "last_updated")
    list_filter = (("study", admin.RelatedOnlyFieldListFilter),)
    search_fields = ("study__short_citation",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study", "term")


@admin.register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    model = models.Result
    form = forms.ResultForm
    list_display = (
        "id",
        "study",
        "design",
        "cause",
        "effect",
        "sort_order",
        "created",
        "last_updated",
    )
    list_filter = (
        ("study", admin.RelatedOnlyFieldListFilter),
        ("design", admin.RelatedOnlyFieldListFilter),
        ("cause", admin.RelatedOnlyFieldListFilter),
        ("effect", admin.RelatedOnlyFieldListFilter),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study", "design", "cause", "effect")
