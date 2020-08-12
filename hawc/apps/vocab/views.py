from django.views.generic import TemplateView


class Widget(TemplateView):
    template_name = "vocab/widgets.html"
