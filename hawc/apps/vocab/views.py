import json
from typing import List

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from django.views.generic import TemplateView

from ..common.crumbs import Breadcrumb
from . import models


def build_ehv_breadcrumbs(user, name: str) -> List[Breadcrumb]:
    return Breadcrumb.build_crumbs(
        user,
        name,
        [Breadcrumb(name="Environmental Health Vocabulary", url=reverse("vocab:ehv-browse"))],
    )


class EhvBrowse(TemplateView):
    template_name = "vocab/ehv_browse.html"

    def _get_config(self) -> str:
        # get EHV in json; use cache if possible
        key = "ehv-dataframe-json"
        data = cache.get(key)
        if data is None:
            data = json.dumps(
                dict(
                    app="animalStartup",
                    page="ehvBrowserStartup",
                    data=dict(data=models.Term.ehv_dataframe().to_csv(index=False)),
                )
            )
            cache.set(key, data, settings.CACHE_10_MIN)
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = self._get_config()
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user, "Environmental Health Vocabulary"
        )
        return context
