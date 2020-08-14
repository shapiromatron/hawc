from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ..common.views import beta_tester_required


class Widget(TemplateView):
    template_name = "vocab/widgets.html"

    @method_decorator(beta_tester_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
