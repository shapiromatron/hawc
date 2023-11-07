import logging
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ..common.htmx import HtmxView
from . import methods

logger = logging.getLogger(__name__)


@method_decorator(staff_member_required, name="dispatch")
class Swagger(TemplateView):
    template_name = "admin/swagger.html"


@method_decorator(staff_member_required, name="dispatch")
class Dashboard(HtmxView):
    actions = {
        "assessment_size",
        "assessment_growth",
        "assessment_profile",
        "growth",
        "users",
        "daily_changes",
    }

    def index(self, request: HttpRequest, *args, **kwargs):
        return render(request, "admin/dashboard.html", {})

    def growth(self, request: HttpRequest, *args, **kwargs):
        form = methods.GrowthForm(data=request.GET)
        df = fig = None
        if form.is_valid():
            df, fig = form.get_data()
        context = dict(form=form, fig=fig, df=df)
        return render(request, "admin/fragments/growth.html", context)

    def users(self, request: HttpRequest, *args, **kwargs):
        return render(
            request,
            "admin/fragments/users.html",
            {
                "growth": methods.user_growth(),
                "active": methods.user_active(),
                "logins": methods.last_login(),
            },
        )

    def assessment_size(self, request: HttpRequest, *args, **kwargs):
        df = methods.size_df()
        html = df.to_html(index=False, table_id="table", escape=False, border=0)
        return render(request, "admin/fragments/assessment_size.html", {"table": html})

    def assessment_growth(self, request: HttpRequest, *args, **kwargs):
        try:
            matrix = methods.growth_matrix().to_html()
        except ValueError:
            matrix = None
        return render(
            request,
            "admin/fragments/assessment_growth.html",
            {"matrix": matrix, "form": methods.AssessmentGrowthSettings()},
        )

    def assessment_profile(self, request: HttpRequest, *args, **kwargs):
        form = methods.AssessmentGrowthSettings(data=request.GET)
        assessment = fig = None
        if form.is_valid():
            assessment, fig = form.time_series()
        return render(
            request,
            "admin/fragments/assessment_profile.html",
            {"form": form, "assessment": assessment, "fig": fig},
        )

    def daily_changes(self, request: HttpRequest, *args, **kwargs):
        data = methods.daily_changes()
        return render(request, "admin/fragments/changes.html", data)


@method_decorator(staff_member_required, name="dispatch")
class MediaPreview(TemplateView):
    template_name = "admin/media_preview.html"

    def get_context_data(self, **kwargs):
        """
        Suffix-specific values were obtained by querying media file extensions:

        ```bash
        find {settings.MEDIA_ROOT} -type f | grep -o ".[^.]\\+$" | sort | uniq -c
        ```
        """
        context = super().get_context_data(**kwargs)
        obj = self.request.GET.get("item", "")
        media = Path(settings.MEDIA_ROOT)
        context["has_object"] = False
        resolved = (media / obj).resolve()
        context["object_name"] = str(Path(obj))
        if obj and resolved.exists() and media in resolved.parents:
            root_uri = self.request.build_absolute_uri(location=settings.MEDIA_URL[:-1])
            uri = resolved.as_uri().replace(media.as_uri(), root_uri)
            context["has_object"] = True
            context["object_uri"] = uri
            context["suffix"] = resolved.suffix.lower()
            if context["suffix"] in [".csv", ".json", ".ris", ".txt"]:
                context["object_text"] = resolved.read_text()
            if context["suffix"] in [".xls", ".xlsx"]:
                df = pd.read_excel(str(resolved))
                context["object_html"] = df.to_html(index=False)
            if context["suffix"] in [".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
                context["object_image"] = True
            if context["suffix"] in [".pdf"]:
                context["object_pdf"] = True

        return context
