from django.conf import settings
from django.views.generic import TemplateView

from ..common.crumbs import Breadcrumb
from ..common.helper import WebappConfig, cacheable
from . import models


class VocabBrowse(TemplateView):
    vocab_name = None
    template_name = None
    vocab_context = None
    data = None

    def _get_config(self) -> str:
        # get EHV in json; use cache if possible
        def get_app_config() -> str:
            return WebappConfig(
                app="animalStartup",
                page="vocabBrowserStartup",
                data={
                    "vocab": self.vocab_name,
                    "data": self.data,
                },
            ).model_dump_json()

        return cacheable(
            get_app_config,
            f"{self.vocab_name}-dataframe-json",
            cache_duration=settings.CACHE_10_MIN,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = self._get_config()
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, self.vocab_context)
        return context


class EhvBrowse(VocabBrowse):
    vocab_name = "ehv"
    template_name = "vocab/ehv_browse.html"
    vocab_context = "Environmental Health Vocabulary"
    data = models.Term.ehv_dataframe().to_csv(index=False)


class ToxrefBrowse(VocabBrowse):
    vocab_name = "toxref"
    template_name = "vocab/toxref_browse.html"
    vocab_context = "ToxRef Database Vocabulary"
    data = models.Term.toxref_dataframe().to_csv(index=False)
