import json

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from . import models


# @method_decorator(cache_page(600), name="dispatch")
class EhvBrowse(TemplateView):
    template_name = "vocab/ehv_browse.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = json.dumps({"data": models.Term.ehv_dataframe().to_csv(index=False)})
        return context
