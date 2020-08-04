from django.views.generic import FormView

from . import forms


class Widget(FormView):
    template_name = "vocab/widgets.html"
    form_class = forms.WidgetForm

