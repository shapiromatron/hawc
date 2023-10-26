from django.conf import settings
from django.views.generic import TemplateView

from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig, cacheable
from . import models


class EhvBrowse(TemplateView):
    template_name = "vocab/ehv_browse.html"

    def _get_config(self) -> str:
        # get EHV in json; use cache if possible
        data = WebappConfig(
            app="animalStartup",
            page="ehvBrowserStartup",
            data={"data": models.Term.ehv_dataframe().to_csv(index=False)},
        ).json()
        return cacheable(lambda: data, "ehv-dataframe-json", cache_duration=settings.CACHE_10_MIN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = self._get_config()
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user, "Environmental Health Vocabulary"
        )
        return context
